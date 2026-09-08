import os
import sys
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configura o path do Python para encontrar as pastas dos Epics
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "Epic01"))
sys.path.insert(0, os.path.join(BASE_DIR, "Epic02"))
sys.path.insert(0, os.path.join(BASE_DIR, "Epic03"))
sys.path.insert(0, os.path.join(BASE_DIR, "Epic04"))
sys.path.insert(0, os.path.join(BASE_DIR, "Epic06"))

# Importações dos módulos desenvolvidos pelo grupo
from epic1 import carregar_palavras, dividir_em_paginas
from epic3 import construir_indice_com_colisoes
from epic4 import buscar_por_indice
from epic6 import calcular_estatisticas

app = FastAPI(title="API - Índice Hash Estático")

# Configuração do CORS para permitir que o React converse com o FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ESTADO GLOBAL EM MEMÓRIA
GLOBAL_PAGINAS = []
GLOBAL_INDICE = None


@app.post("/load-data")
def route_load_data(params: dict):
    global GLOBAL_PAGINAS, GLOBAL_INDICE
    page_size = params.get("pageSize", 1000)
    
    file_path = os.path.join(BASE_DIR, "Arquivo.Txt", "words.txt")
    palavras = carregar_palavras(file_path)
    
    if not palavras:
        return {"error": "Não foi possível carregar o arquivo words.txt"}

    # Executa a lógica real do Epic 01
    GLOBAL_PAGINAS = dividir_em_paginas(palavras, page_size)
    GLOBAL_INDICE = None  # Reseta o índice antigo pois o tamanho de página mudou

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


@app.post("/build-index")
def route_build_index(params: dict):
    global GLOBAL_PAGINAS, GLOBAL_INDICE
    bucket_capacity = params.get("bucketCapacity", 10)

    if not GLOBAL_PAGINAS:
        return {"error": "Carregue os dados antes de construir o índice."}

    # Executa a lógica real do Epic 03 (construção com colisões/overflow)
    GLOBAL_INDICE = construir_indice_com_colisoes(GLOBAL_PAGINAS, bucket_capacity)

    # Executa a lógica real do Epic 06 (métricas e taxas de colisão/overflow)
    stats = calcular_estatisticas(GLOBAL_INDICE)

    # Prepara a amostra de buckets para o Visualizador do React (CA28)
    # Seleciona os primeiros 6 buckets para exibição no grid
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


@app.post("/search")
def route_search(params: dict):
    global GLOBAL_PAGINAS, GLOBAL_INDICE
    key = params.get("key", "").strip()

    if not GLOBAL_INDICE or not GLOBAL_PAGINAS:
        return {"error": "Construa o índice antes de realizar buscas."}

    # 1. Busca por Índice Real (Epic 04)
    resultado_indice = buscar_por_indice(key, GLOBAL_INDICE, GLOBAL_PAGINAS)

    # 2. Table Scan Real (Varredura Sequencial de Comparação)
    scan_inicio = time.perf_counter()
    scan_found = False
    scan_page = None
    scan_pages_read = 0

    for i, pagina in enumerate(GLOBAL_PAGINAS):
        scan_pages_read += 1
        if key in pagina:
            scan_found = True
            scan_page = i + 1
            break
            
    scan_fim = time.perf_counter()
    scan_time_ms = (scan_fim - scan_inicio) * 1000

    # Formata a resposta combinada para a tabela do React
    return {
        "index": {
            "found": resultado_indice["encontrada"],
            "key": key,
            "pageNumber": (resultado_indice["pagina"] + 1) if resultado_indice["pagina"] is not None else -1,
            "bucketIndex": resultado_indice["bucket"],
            "costPagesRead": resultado_indice["custo_paginas"],
            "timeMs": round(resultado_indice["tempo_segundos"] * 1000, 4)
        },
        "scan": {
            "found": scan_found,
            "key": key,
            "pageNumber": scan_page if scan_found else -1,
            "costPagesRead": scan_pages_read,
            "timeMs": round(scan_time_ms, 4)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)