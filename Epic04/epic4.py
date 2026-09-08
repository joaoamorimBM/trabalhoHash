# -*- coding: utf-8 -*-

"""
============================================================================
EPIC 4 - PESQUISA POR INDICE
============================================================================

HU09 - Buscar uma chave usando o indice

Responsabilidades deste modulo:

RN18:
- A chave de busca sera recebida da interface grafica.

RN19:
1. aplicar a funcao hash na chave;
2. localizar o bucket correspondente;
3. recuperar o endereco da pagina;
4. carregar a pagina;
5. localizar a tupla dentro da pagina.

CA19:
- informar se a chave foi encontrada;
- informar em qual pagina ela esta;
- informar o custo estimado em leituras de pagina.

CA20:
- caso a chave nao exista, informar que ela nao foi encontrada.

Este modulo reutiliza:
- funcao hash do EPIC 2;
- indice com tratamento de colisao/overflow do EPIC 3;
- paginas criadas a partir dos dados do EPIC 1.
============================================================================
"""

import os
import sys
import time


# ===========================================================================
# IMPORTACAO DOS EPICS ANTERIORES
# ===========================================================================

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(_BASE, "Epic01"))
sys.path.insert(0, os.path.join(_BASE, "Epic02"))
sys.path.insert(0, os.path.join(_BASE, "Epic03"))

from epic2 import carregar_palavras, dividir_em_paginas, funcao_hash
from epic3 import construir_indice_com_colisoes


# ===========================================================================
# HU09 - BUSCA UTILIZANDO O INDICE HASH
# ===========================================================================

def buscar_por_indice(chave, indice, paginas):
    """
    Realiza uma busca completa utilizando o indice hash.

    Fluxo exigido pela RN19:
        chave
          -> funcao hash
          -> bucket
          -> endereco da pagina
          -> leitura da pagina
          -> confirmacao da tupla

    Retorna um dicionario para facilitar a futura integracao com
    a interface grafica.

    Parametros:
        chave (str):
            Palavra procurada.

        indice (IndiceComColisao):
            Indice hash previamente construido.

        paginas (list):
            Lista das paginas de dados criadas pelo EPIC 1.

    Retorno:
        dict contendo:
            - chave
            - encontrada
            - bucket
            - pagina
            - custo_paginas
            - tempo_segundos
            - mensagem
    """

    inicio = time.perf_counter()

    # -----------------------------------------------------------------------
    # RN19 - PASSO 1
    # Aplicar a funcao hash na chave.
    # -----------------------------------------------------------------------

    endereco_bucket = funcao_hash(chave, indice.nb)

    # -----------------------------------------------------------------------
    # RN19 - PASSO 2
    # Localizar o bucket calculado pela funcao hash.
    # -----------------------------------------------------------------------

    bucket = indice.buckets[endereco_bucket]

    # -----------------------------------------------------------------------
    # RN19 - PASSO 3
    # Procurar a chave no bucket.
    #
    # O metodo buscar() do EPIC 3 verifica:
    # - area principal;
    # - cadeia de overflow.
    #
    # Caso encontre, retorna o numero da pagina.
    # Caso contrario, retorna None.
    # -----------------------------------------------------------------------

    numero_pagina = bucket.buscar(chave)

    # -----------------------------------------------------------------------
    # CA20
    # Se nao existe no indice, nenhuma pagina de dados precisa ser carregada.
    # -----------------------------------------------------------------------

    if numero_pagina is None:
        fim = time.perf_counter()

        return {
            "chave": chave,
            "encontrada": False,
            "bucket": endereco_bucket,
            "pagina": None,
            "custo_paginas": 0,
            "tempo_segundos": fim - inicio,
            "mensagem": "Chave nao encontrada."
        }

    # -----------------------------------------------------------------------
    # RN19 - PASSO 4
    # Carregar a pagina apontada pelo indice.
    #
    # Neste projeto as paginas estao simuladas em memoria.
    # Acessar paginas[numero_pagina] representa uma leitura da pagina.
    # -----------------------------------------------------------------------

    pagina = paginas[numero_pagina]

    custo_paginas = 1

    # -----------------------------------------------------------------------
    # RN19 - PASSO 5
    # Confirmar que a tupla realmente existe na pagina informada pelo indice.
    # -----------------------------------------------------------------------

    encontrada = chave in pagina

    fim = time.perf_counter()

    # -----------------------------------------------------------------------
    # CA19
    # Monta o resultado da busca.
    # -----------------------------------------------------------------------

    if encontrada:
        mensagem = f"Chave encontrada na pagina {numero_pagina}."
    else:
        # Este caso indicaria uma inconsistencia entre o indice e as paginas.
        mensagem = (
            "A chave foi localizada no indice, mas nao foi encontrada "
            "na pagina indicada."
        )

    return {
        "chave": chave,
        "encontrada": encontrada,
        "bucket": endereco_bucket,
        "pagina": numero_pagina,
        "custo_paginas": custo_paginas,
        "tempo_segundos": fim - inicio,
        "mensagem": mensagem
    }


# ===========================================================================
# DEMONSTRACAO
# ===========================================================================

def _demonstracao():
    """
    Demonstra o funcionamento do EPIC 4 utilizando o arquivo real
    do trabalho.

    Esta funcao existe apenas para teste/apresentacao.
    Posteriormente a interface grafica chamara buscar_por_indice().
    """

    print("=" * 70)
    print(" EPIC 4 - PESQUISA POR INDICE")
    print("=" * 70)

    caminho = os.path.join(_BASE, "Arquivo.Txt", "words.txt")

    tamanho_pagina = 1000
    fr = 20

    # -----------------------------------------------------------------------
    # EPIC 1
    # Carregar arquivo e criar paginas.
    # -----------------------------------------------------------------------

    palavras = carregar_palavras(caminho)

    if palavras is None:
        print("ERRO: nao foi possivel carregar o arquivo.")
        return

    paginas = dividir_em_paginas(palavras, tamanho_pagina)

    # -----------------------------------------------------------------------
    # EPIC 2 + EPIC 3
    # Construir indice com tratamento de colisao e overflow.
    # -----------------------------------------------------------------------

    indice = construir_indice_com_colisoes(paginas, fr)

    print(f"Total de registros........: {len(palavras)}")
    print(f"Total de paginas..........: {len(paginas)}")
    print(f"FR........................: {fr}")
    print(f"NB........................: {indice.nb}")

    # -----------------------------------------------------------------------
    # BUSCA 1
    # Palavra existente na primeira pagina.
    # -----------------------------------------------------------------------

    chave = palavras[0]

    resultado = buscar_por_indice(chave, indice, paginas)

    print("\n--- TESTE 1: chave existente ---")
    mostrar_resultado(resultado)

    # -----------------------------------------------------------------------
    # BUSCA 2
    # Palavra existente perto do final do arquivo.
    # -----------------------------------------------------------------------

    chave = palavras[-1]

    resultado = buscar_por_indice(chave, indice, paginas)

    print("\n--- TESTE 2: chave existente no final do arquivo ---")
    mostrar_resultado(resultado)

    # -----------------------------------------------------------------------
    # BUSCA 3
    # Encontrar automaticamente uma chave que foi armazenada em overflow.
    #
    # Isso demonstra que o EPIC 4 consegue pesquisar corretamente mesmo
    # quando houve colisao.
    # -----------------------------------------------------------------------

    chave_overflow = encontrar_chave_em_overflow(indice)

    if chave_overflow is not None:
        resultado = buscar_por_indice(
            chave_overflow,
            indice,
            paginas
        )

        print("\n--- TESTE 3: chave armazenada em overflow ---")
        mostrar_resultado(resultado)

    # -----------------------------------------------------------------------
    # BUSCA 4
    # Chave que nao existe.
    # -----------------------------------------------------------------------

    chave = "__CHAVE_QUE_NAO_EXISTE_NO_ARQUIVO__"

    resultado = buscar_por_indice(chave, indice, paginas)

    print("\n--- TESTE 4: chave inexistente ---")
    mostrar_resultado(resultado)

    # -----------------------------------------------------------------------
    # BUSCA INTERATIVA
    # Permite ao usuario digitar uma chave manualmente.
    #
    # Na aplicacao final essa entrada sera feita pela interface grafica.
    # -----------------------------------------------------------------------

    print("\n--- BUSCA INTERATIVA ---")

    chave_digitada = input("Digite uma chave para buscar no indice: ").strip()

    if chave_digitada:
        resultado = buscar_por_indice(
            chave_digitada,
            indice,
            paginas
        )

        mostrar_resultado(resultado)

    else:
        print("Nenhuma chave foi informada.")

    print("=" * 70)


# ===========================================================================
# FUNCOES AUXILIARES DA DEMONSTRACAO
# ===========================================================================

def encontrar_chave_em_overflow(indice):
    """
    Procura uma chave que esteja armazenada em algum no de overflow.

    Utilizada apenas para demonstrar que a busca do EPIC 4 funciona
    tambem quando uma colisao ocorreu.
    """

    for bucket in indice.buckets:

        no = bucket.overflow

        if no is not None and len(no.entradas) > 0:
            chave, _ = no.entradas[0]
            return chave

    return None


def mostrar_resultado(resultado):
    """
    Exibe um resultado de busca no terminal.

    A interface grafica posteriormente podera utilizar diretamente
    o dicionario retornado por buscar_por_indice().
    """

    print(f"Chave.....................: {resultado['chave']}")
    print(f"Encontrada.................: {resultado['encontrada']}")
    print(f"Bucket acessado............: {resultado['bucket']}")

    if resultado["pagina"] is not None:
        print(f"Pagina.....................: {resultado['pagina']}")
    else:
        print("Pagina.....................: nenhuma")

    print(
        f"Custo (paginas lidas)......: "
        f"{resultado['custo_paginas']}"
    )

    print(
        f"Tempo de busca..............: "
        f"{resultado['tempo_segundos']:.9f} segundos"
    )

    print(f"Resultado...................: {resultado['mensagem']}")


# ===========================================================================
# EXECUCAO DIRETA
# ===========================================================================

if __name__ == "__main__":
    _demonstracao()