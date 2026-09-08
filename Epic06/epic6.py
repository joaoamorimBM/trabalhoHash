# -*- coding: utf-8 -*-
"""
============================================================================
 EPIC 6 - ESTATISTICAS E METRICAS
============================================================================

Autor da parte: Isaac Newton
Disciplina: Projeto de Banco de Dados

Este modulo implementa a parte do EPIC 6 do trabalho. Ele e responsavel por
CALCULAR e apresentar as taxas percentuais de colisao e de overflow do
indice hash estatico, a partir das CONTAGENS que o EPIC 3 ja produz.

O EPIC 6 e dividido em 2 historias de usuario:

  HU12 - Calcular taxa de colisoes
         (RN24: calcular e exibir a taxa de colisoes em %;
          CA25: a interface mostra o percentual apos construir o indice)

  HU13 - Calcular taxa de overflow
         (RN25: calcular e exibir a taxa de overflow em %;
          CA26: a interface mostra o percentual apos construir o indice)

Formulas usadas pela equipe:

  taxa_de_colisoes (%)  = (total de colisoes / NR) x 100
      -> NR = numero total de registros (chaves) inseridos no indice.
      -> Cada colisao representa 1 chave que precisou ir para a area de
         overflow porque o bucket dela ja estava cheio (ver EPIC 3, RN14).

  taxa_de_overflow (%)  = (buckets que entraram em overflow / NB) x 100
      -> NB = numero total de buckets do indice.
      -> Um bucket "entra em overflow" quando precisa de pelo menos um
         no extra encadeado (ver EPIC 3, HU08).

Observacoes de escopo:
  - QUEM CONTA as colisoes e os buckets em overflow, evento por evento, e o
    EPIC 3 (HU07/HU08). Aqui no EPIC 6 nos so pegamos essas contagens
    prontas e transformamos em PORCENTAGEM (a metrica em si).
  - A CONSTRUCAO do indice (paginas, buckets, funcao hash) e dos EPICs 1 e 2.
  - Mostrar essas taxas dentro da INTERFACE GRAFICA final e o EPIC 7; aqui
    fica pronta a funcao que calcula os numeros que a tela vai exibir.

----------------------------------------------------------------------------
SOBRE OS "MOCKS" (dados/funcoes de outros EPICs ainda nao integrados)
----------------------------------------------------------------------------
Assim como o EPIC 3 fez em relacao aos EPICs 1 e 2, este arquivo tenta
importar a construcao do indice (com colisao/overflow) do EPIC 3 e, se a
pasta Epic03/ ainda nao estiver mesclada nesta branch, usa uma versao
MOCADA equivalente (mesmas formulas e mesmo algoritmo de overflow em
cadeia) so para o EPIC 6 poder ser testado e apresentado de forma
independente.

  -> Quando as branches forem integradas, o import real passa a funcionar
     sozinho e o bloco de fallback deixa de ser usado.
============================================================================
"""

import os
import sys
import random


# ---------------------------------------------------------------------------
# DEPENDENCIA DO EPIC 3 (com MOCK/fallback enquanto nao integrado)
# ---------------------------------------------------------------------------
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BASE, "Epic03"))

try:
    # Caminho "de verdade": reaproveita a construcao do indice do EPIC 3
    # (que por sua vez ja reaproveita os EPICs 1 e 2 internamente).
    from epic3 import (
        carregar_palavras,
        dividir_em_paginas,
        construir_indice_com_colisoes,
        _gerar_dados_mock,
    )
    _USANDO_MOCK = False
except Exception:  # pragma: no cover - EPIC 3 ainda nao integrado nesta branch
    _USANDO_MOCK = True

    def funcao_hash(chave, nb):
        """MOCK do EPIC 2 (HU05). Mesmo hash polinomial combinado pela equipe."""
        h = 0
        for letra in chave:
            h = (h * 31 + ord(letra)) % nb
        return h

    def carregar_palavras(caminho):
        """MOCK do EPIC 1 (HU01)."""
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return arquivo.read().splitlines()
        except Exception:
            print("ERRO: nao foi possivel ler o arquivo.")
            return None

    def dividir_em_paginas(palavras, tamanho_pagina):
        """MOCK do EPIC 1 (HU03)."""
        paginas = []
        for inicio in range(0, len(palavras), tamanho_pagina):
            paginas.append(palavras[inicio:inicio + tamanho_pagina])
        return paginas

    def _gerar_dados_mock(quantidade=2000, tamanho_pagina=100, semente=42):
        """MOCK de massa de dados, identico ao usado no EPIC 3."""
        rng = random.Random(semente)
        alfabeto = "abcdefghijklmnopqrstuvwxyz"
        palavras = []
        for i in range(quantidade):
            tamanho = rng.randint(3, 10)
            palavras.append("".join(rng.choice(alfabeto) for _ in range(tamanho)) + str(i))
        return dividir_em_paginas(palavras, tamanho_pagina)

    class _BucketMock:
        """MOCK simplificado do BucketComColisao do EPIC 3 (mesmo algoritmo:
        area principal de capacidade FR + cadeia de overflow encadeado)."""

        def __init__(self, capacidade):
            self.capacidade = capacidade
            self.entradas = []
            self.overflow_nos = []  # lista de listas, cada uma cap. FR
            self.colisoes = 0

        def inserir(self, chave, pagina):
            if len(self.entradas) < self.capacidade:
                self.entradas.append((chave, pagina))
                return
            self.colisoes += 1
            for no in self.overflow_nos:
                if len(no) < self.capacidade:
                    no.append((chave, pagina))
                    return
            self.overflow_nos.append([(chave, pagina)])

        def esta_em_overflow(self):
            return len(self.overflow_nos) > 0

        def total_registros(self):
            return len(self.entradas) + sum(len(no) for no in self.overflow_nos)

    class _IndiceMock:
        """MOCK simplificado do IndiceComColisao do EPIC 3."""

        def __init__(self, nr, fr):
            self.nr = nr
            self.fr = fr
            self.nb = (nr // fr) + 1
            self.buckets = [_BucketMock(fr) for _ in range(self.nb)]
            self.tempo_construcao = None

        def inserir(self, chave, pagina):
            endereco = funcao_hash(chave, self.nb)
            self.buckets[endereco].inserir(chave, pagina)

        def total_colisoes(self):
            return sum(b.colisoes for b in self.buckets)

        def total_buckets_em_overflow(self):
            return sum(1 for b in self.buckets if b.esta_em_overflow())

        def total_registros_indexados(self):
            return sum(b.total_registros() for b in self.buckets)

    def construir_indice_com_colisoes(paginas, fr):
        """MOCK do EPIC 3 (HU06/HU07/HU08): mesma logica, versao simplificada."""
        import time
        nr = sum(len(pagina) for pagina in paginas)
        indice = _IndiceMock(nr, fr)
        inicio = time.perf_counter()
        for numero_pagina, pagina in enumerate(paginas):
            for chave in pagina:
                indice.inserir(chave, numero_pagina)
        indice.tempo_construcao = time.perf_counter() - inicio
        return indice


# ===========================================================================
# HU12 - TAXA DE COLISOES (%)
# ===========================================================================
def taxa_de_colisoes(indice):
    """
    Calcula a taxa de colisoes (RN24), em porcentagem:

        taxa = (total de colisoes / NR) x 100

    Uma colisao (definida no EPIC 3 / RN14) e cada chave que precisou ir
    para a area de overflow porque o bucket dela ja estava com a area
    principal cheia. Dividimos pelo NUMERO DE REGISTROS (NR), pois a taxa
    representa "de cada 100 chaves inseridas, quantas colidiram".
    """
    if indice.nr == 0:
        return 0.0
    return (indice.total_colisoes() / indice.nr) * 100


# ===========================================================================
# HU13 - TAXA DE OVERFLOW (%)
# ===========================================================================
def taxa_de_overflow(indice):
    """
    Calcula a taxa de overflow (RN25), em porcentagem:

        taxa = (buckets em overflow / NB) x 100

    Diferente da taxa de colisao (que conta CHAVES), a taxa de overflow
    conta BUCKETS: de cada 100 buckets criados, quantos precisaram de pelo
    menos um no de overflow encadeado (EPIC 3 / HU08). Serve para avaliar
    se FR e NB foram bem dimensionados (RN09/RN08).
    """
    if indice.nb == 0:
        return 0.0
    return (indice.total_buckets_em_overflow() / indice.nb) * 100


def calcular_estatisticas(indice):
    """
    Reune num unico dicionario tudo que a interface grafica (EPIC 7) vai
    precisar exibir sobre colisao e overflow (CA25/CA26). Facilita a
    integracao: a tela so precisa chamar esta funcao e ler os campos.
    """
    return {
        "nr": indice.nr,
        "nb": indice.nb,
        "fr": indice.fr,
        "total_colisoes": indice.total_colisoes(),
        "total_buckets_em_overflow": indice.total_buckets_em_overflow(),
        "taxa_colisoes_pct": taxa_de_colisoes(indice),
        "taxa_overflow_pct": taxa_de_overflow(indice),
        "tempo_construcao_seg": indice.tempo_construcao,
    }


# ===========================================================================
# DEMONSTRACAO (para apresentar e testar a parte do EPIC 6)
# ===========================================================================
def _demonstracao():
    """
    Roda o EPIC 6 de ponta a ponta:
      - constroi o indice com tratamento de colisao/overflow (EPIC 3, real
        ou mocado);
      - calcula e exibe a taxa de colisoes (HU12) e a taxa de overflow
        (HU13);
      - repete o calculo para alguns valores de FR, so para ilustrar como
        a escolha de FR/NB muda as duas taxas (RN09).
    """
    caminho = os.path.join(_BASE, "Arquivo.Txt", "words.txt")
    tamanho_pagina = 1000

    print("=" * 70)
    print(" EPIC 6 - ESTATISTICAS E METRICAS (taxa de colisao e de overflow)")
    print("=" * 70)
    if _USANDO_MOCK:
        print("[AVISO] EPIC 3 ainda nao integrado nesta branch.")
        print("        Usando construcao de indice MOCADA (mesmo algoritmo)")
        print("        ate o merge da branch Epic3 acontecer.")
        print()

    palavras = carregar_palavras(caminho)
    if palavras:
        paginas = dividir_em_paginas(palavras, tamanho_pagina)
    else:
        print("[AVISO] Arquivo de palavras nao encontrado em:", caminho)
        print("        Gerando massa de dados MOCADA apenas para a demo.")
        paginas = _gerar_dados_mock()

    nr = sum(len(p) for p in paginas)
    print("Total de registros (NR):", nr, " | Paginas:", len(paginas))
    print()

    # FR pequeno de proposito na demo, para as taxas nao ficarem em 0%.
    for fr in (10, 20, 50):
        indice = construir_indice_com_colisoes(paginas, fr)
        stats = calcular_estatisticas(indice)

        print("--- FR = %d  (NB = %d) ---" % (fr, stats["nb"]))
        print("HU12 - Taxa de colisoes.....: %.2f%%  (%d colisoes em %d registros)"
              % (stats["taxa_colisoes_pct"], stats["total_colisoes"], stats["nr"]))
        print("HU13 - Taxa de overflow.....: %.2f%%  (%d de %d buckets)"
              % (stats["taxa_overflow_pct"], stats["total_buckets_em_overflow"], stats["nb"]))
        print("Tempo de construcao.........: %.3f segundos" % stats["tempo_construcao_seg"])
        print()

    print("Conclusao esperada: quanto MENOR o FR (para o mesmo NR), MAIOR")
    print("tende a ser a taxa de colisao/overflow - por isso a equipe deve")
    print("dimensionar FR e NB com cuidado (RN08/RN09).")
    print("=" * 70)


if __name__ == "__main__":
    _demonstracao()
