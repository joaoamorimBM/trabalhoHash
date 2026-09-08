# -*- coding: utf-8 -*-
"""
============================================================================
 EPIC 7 - INTERFACE GRÁFICA E INTEGRAÇÃO UNIFICADA (API REST)
============================================================================

Autor da parte: Luís Eduardo Barrocas
Disciplina: Projeto de Banco de Dados

Este módulo implementa o EPIC 7 do trabalho e o servidor central da aplicação.
Ele é responsável por expor uma API REST em Python (FastAPI) para integrar o
front-end moderno em React (Vite) aos algoritmos de todos os EPICs anteriores
(EPICs 1 a 6), permitindo a execução unificada do sistema sem a necessidade de
inicializações manuais isoladas.

O EPIC 7 atende às seguintes Histórias de Usuário e Critérios de Aceitação:

  HU14 / HU15 - Painel de Controle e Parâmetros
         (CA04: entrada customizável para tamanho de página;
          CA05: entrada customizável para capacidade do bucket FR)

  HU16 / HU17 - Visualização de Páginas e Métricas do Índice
         (CA07/CA25/CA26: exibe a estrutura de primeira/última página e apresenta
          a taxa de colisões %, taxa de overflow % e tempo de construção em ms)

  HU18 - Visualizador de Buckets
         (CA28: exibe uma grade organizada/paginada dos buckets e seu conteúdo)

  HU19 - Pesquisa de Chave e Destaque Visual de Acesso
         (CA19/CA21/CA23/CA24: apresenta a tabela comparativa entre Busca por Índice
          e Table Scan com tempos em milissegundos e contagem de leituras de disco;
          CA29: destaca em cor verde o card do bucket e exibe a página acessada)

Responsabilidades deste módulo (server.py):
  - Criar os endpoints HTTP (/load-data, /build-index, /search).
  - Manter o estado global em memória durante a sessão (massa de páginas e índice).
  - Executar as funções reais dos EPICs 1, 3, 4, 5 e 6 a cada requisição do React.
  - Tratar requisições Cross-Origin (CORS) enviadas pelo servidor Vite (porta 5173).

Este módulo reutiliza:
  - Carga de dados e paginação do EPIC 1;
  - Função hash do EPIC 2;
  - Construção do índice com tratamento de colisões e overflow do EPIC 3;
  - Busca por índice hash do EPIC 4;
  - Varredura sequencial (Table Scan) e métricas comparativas do EPIC 5;
  - Cálculo percentual das taxas do EPIC 6.
============================================================================
"""

import os
import sys
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ===========================================================================
# IMPORTAÇÃO DOS MÓDULOS DESENVOLVIDOS PELA EQUIPE (EPICs 1 a 6)
# ===========================================================================

from Epic01.epic1 import carregar_palavras, dividir_em_paginas
from Epic03.epic3 import construir_indice_com_colisoes
from Epic04.epic4 import buscar_por_indice
from Epic05.epic5 import table_scan
from Epic06.epic6 import calcular_estatisticas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="API - Índice Hash Estático")

# Configuração do CORS para permitir que o React converse com o FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# ESTADO GLOBAL EM MEMÓRIA
# Mantém a estrutura de páginas e o índice ativo para ser consultado pela API
# ---------------------------------------------------------------------------
GLOBAL_PAGINAS = []
GLOBAL_INDICE = None


# ===========================================================================
# ENDPOINT 1 - CARGA DE DADOS E PAGINAÇÃO (EPIC 1)
# ===========================================================================

@app.post("/load-data")
def route_load_data(params: dict):
    """
    Carrega o arquivo words.txt e divide os registros em páginas de tamanho
    customizado informado pela interface gráfica (CA04 / CA07).
    """
    global GLOBAL_PAGINAS, GLOBAL_INDICE
    page_size = params.get("pageSize", 1000)
    
    file_path = os.path.join(BASE_DIR, "Arquivo.Txt", "words.txt")
    palavras = carregar_palavras(file_path)
    
    if not palavras:
        return {"error": "Não foi possível carregar o arquivo words.txt"}

    GLOBAL_PAGINAS = dividir_em_paginas(palavras, page_size)
    GLOBAL_INDICE = None  # Reseta o índice prévio para forçar reconstrução com a nova paginação

    return {
        "totalWords": len(palavras),
        "totalPages": len(GLOBAL_PAGINAS),
        "pageSize": page_size,
        "firstPage": {
            "pageNumber": 1,
            "records": GLOBAL_PAGINAS[0][:5] if GLOBAL_PAGINAS else []
        },
        "lastPage": {
            "pageNumber": len(GLOBAL_PAGINAS),
            "records": GLOBAL_PAGINAS[-1][:5] if GLOBAL_PAGINAS else []
        }
    }


# ===========================================================================
# ENDPOINT 2 - CONSTRUÇÃO DO ÍNDICE E MÉTRICAS (EPICs 2, 3 e 6)
# ===========================================================================

@app.post("/build-index")
def route_build_index(params: dict):
    """
    Constrói a tabela hash usando a capacidade FR fornecida e calcula as taxas
    de colisão e overflow para exibição no painel de estatísticas (CA05/CA25/CA26/CA28).
    """
    global GLOBAL_PAGINAS, GLOBAL_INDICE
    bucket_capacity = params.get("bucketCapacity", 10)

    if not GLOBAL_PAGINAS:
        return {"error": "Carregue os dados antes de construir o índice."}

    # Executa a construção real do índice tratando colissões (EPIC 3)
    GLOBAL_INDICE = construir_indice_com_colisoes(GLOBAL_PAGINAS, bucket_capacity)
    
    # Calcula as taxas e estatísticas reais (EPIC 6)
    stats = calcular_estatisticas(GLOBAL_INDICE)

    # Amostra dos primeiros buckets para o Visualizador de Buckets no React (CA28)
    buckets_sample = []
    for i, bucket in enumerate(GLOBAL_INDICE.buckets[:6]):
        keys_data = [{"key": pair[0], "page": pair[1] + 1} for pair in bucket.entradas]
        buckets_sample.append({
            "id": i,
            "keys": keys_data
        })

    return {
        "totalBuckets": stats["nb"],
        "bucketCapacity": stats["fr"],
        "buildTimeMs": round(stats["tempo_construcao_seg"] * 1000, 2),
        "collisionRate": round(stats["taxa_colisoes_pct"], 2),
        "overflowRate": round(stats["taxa_overflow_pct"], 2),
        "bucketsPage": buckets_sample
    }


# ===========================================================================
# ENDPOINT 3 - PESQUISA DE CHAVE E COMPARAÇÃO (EPICs 4 e 5)
# ===========================================================================

@app.post("/search")
def route_search(params: dict):
    """
    Executa a busca por índice e o table scan simultaneamente, retornando a
    tabela comparativa de tempos/custos e indicando o bucket a ser destacado (CA19/CA29).
    """
    global GLOBAL_PAGINAS, GLOBAL_INDICE
    key = params.get("key", "").strip()

    if not GLOBAL_INDICE or not GLOBAL_PAGINAS:
        return {"error": "Construa o índice antes de realizar buscas."}

    # 1. Busca por Índice Real (EPIC 4)
    resultado_indice = buscar_por_indice(key, GLOBAL_INDICE, GLOBAL_PAGINAS)

    # 2. Table Scan Sequencial Real (EPIC 5)
    scan_inicio = time.perf_counter()
    pagina_scan = table_scan(GLOBAL_PAGINAS, key)
    scan_fim = time.perf_counter()

    scan_found = pagina_scan is not None
    scan_pages_read = (pagina_scan + 1) if scan_found else len(GLOBAL_PAGINAS)
    scan_time_ms = (scan_fim - scan_inicio) * 1000
    index_time_ms = resultado_indice["tempo_segundos"] * 1000

    # 3. Métricas Comparativas Percentuais (EPIC 5)
    custo_indice = resultado_indice["custo_paginas"]
    reducao_custo_pct = round(((scan_pages_read - custo_indice) / scan_pages_read * 100), 2) if scan_pages_read > 0 else 0.0
    diferenca_tempo_pct = round(((scan_time_ms - index_time_ms) / index_time_ms * 100), 2) if index_time_ms > 0 else 0.0

    return {
        "index": {
            "found": resultado_indice["encontrada"],
            "key": key,
            "pageNumber": (resultado_indice["pagina"] + 1) if resultado_indice["pagina"] is not None else -1,
            "bucketIndex": resultado_indice["bucket"],
            "costPagesRead": custo_indice,
            "timeMs": round(index_time_ms, 4)
        },
        "scan": {
            "found": scan_found,
            "key": key,
            "pageNumber": (pagina_scan + 1) if scan_found else -1,
            "costPagesRead": scan_pages_read,
            "timeMs": round(scan_time_ms, 4)
        },
        "comparison": {
            "costReductionPct": reducao_custo_pct,
            "timeDifferencePct": diferenca_tempo_pct
        }
    }


# ===========================================================================
# EXECUÇÃO DO SERVIDOR UNIFICADO
# ===========================================================================

if __name__ == "__main__":
    import uvicorn
    # Inicializa o servidor FastAPI na porta local 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)