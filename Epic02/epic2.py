# -*- coding: utf-8 -*-
"""
============================================================================
 EPIC 2 - CONSTRUÇÃO DO ÍNDICE HASH ESTÁTICO
============================================================================

Autor da parte: Vinicius Andrade
Disciplina: Projeto de Banco de Dados

Este módulo implementa a parte do EPIC 2 do trabalho. Ele é responsável por
CONSTRUIR o índice hash estático em cima das páginas que o EPIC 1 já criou.

O EPIC 2 é dividido em 3 histórias de usuário:

  HU04 - Criar os buckets do índice
         (calcular NB, definir FR e criar os NB buckets de capacidade FR)

  HU05 - Implementar uma função hash PRÓPRIA
         (feita pela equipe, sem usar a função hash pronta da linguagem;
          determinística e sempre dentro do intervalo [0 .. NB-1])

  HU06 - Construir o índice percorrendo as páginas
         (para cada palavra: aplica a hash e guarda no bucket a chave e o
          endereço/numero da página onde a palavra está)

Observações de escopo:
  - CARREGAR o arquivo e DIVIDIR em páginas é o EPIC 1 (feito por outra pessoa).
    Aqui a gente só REUSA essas funções para conseguir as páginas.
  - CONTAR e mostrar a "taxa de colisões %" e "taxa de overflow %" é o EPIC 3
    e o EPIC 6. Aqui a estrutura já fica pronta para isso, mas o cálculo das
    porcentagens NÃO é feito nesta parte.
  - BUSCAR usando o índice é o EPIC 4. Este módulo traz uma busca minúscula
    apenas para PROVAR que o índice ficou correto (verificação), não é a
    tela/funcionalidade final de busca.
============================================================================
"""

import os
import sys
import time


# ---------------------------------------------------------------------------
# DEPENDÊNCIA DO EPIC 1
# ---------------------------------------------------------------------------
# O EPIC 2 precisa das páginas prontas. Quem gera as páginas é o EPIC 1.
# Tentamos importar as funções do EPIC 1 (arquivo Epic01/epic1.py). Se por
# algum motivo o arquivo não estiver acessível, definimos uma versão mínima
# de emergência (idêntica em comportamento) só para o EPIC 2 conseguir rodar
# sozinho. As funções abaixo NÃO fazem parte da nota do EPIC 2 - são do EPIC 1.
# ---------------------------------------------------------------------------
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BASE, "Epic01"))
try:
    from epic1 import carregar_palavras, dividir_em_paginas  # EPIC 1
except Exception:  # pragma: no cover - fallback de emergência
    def carregar_palavras(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return arquivo.read().splitlines()
        except Exception:
            print("ERRO: não foi possível ler o arquivo.")
            return None

    def dividir_em_paginas(palavras, tamanho_pagina):
        paginas = []
        for inicio in range(0, len(palavras), tamanho_pagina):
            paginas.append(palavras[inicio:inicio + tamanho_pagina])
        return paginas


# ===========================================================================
# HU05 - FUNÇÃO HASH PRÓPRIA (feita pela equipe)
# ===========================================================================
def funcao_hash(chave, nb):
    """
    Transforma uma palavra (chave) em um número de bucket entre 0 e NB-1.

    Como funciona (hash polinomial - construído pela equipe, NÃO é o hash()
    pronto do Python):
      - Começamos com um acumulador h = 0.
      - Para cada letra da palavra pegamos o seu código numérico (ord(letra))
        e fazemos:  h = (h * 31 + codigo_da_letra) % nb
      - O número 31 é um multiplicador clássico (número primo) que ajuda a
        "espalhar" bem as palavras pelos buckets e diminuir colisões.
      - O "% nb" (resto da divisão por NB) em cada passo garante duas coisas:
          1) o número nunca cresce demais;
          2) o resultado SEMPRE cai no intervalo válido [0 .. NB-1].

    Propriedades exigidas pelo trabalho:
      - DETERMINÍSTICA (RNF05 / CA11): a mesma palavra sempre gera o mesmo
        bucket, porque a conta é sempre a mesma.
      - DENTRO DO INTERVALO (CA12): por causa do "% nb", o retorno está
        sempre em [0 .. NB-1].

    Parâmetros:
      chave (str): a palavra que queremos endereçar.
      nb (int): a quantidade total de buckets.

    Retorna:
      int: o endereço do bucket (0 <= retorno < nb).
    """
    h = 0
    for letra in chave:
        h = (h * 31 + ord(letra)) % nb
    return h


# ===========================================================================
# HU04 - ESTRUTURA DOS BUCKETS
# ===========================================================================
class Bucket:
    """
    Um bucket é uma "gavetinha" do índice. Ele guarda pares (chave -> página).

    - capacidade (FR): quantas chaves cabem no bucket principal.
    - entradas: a lista de pares que couberam dentro da capacidade FR.
    - overflow: a lista de pares que passaram do FR (transbordamento).

    Sobre o 'overflow' aqui:
      Para o índice conter TODOS os registros (CA13), nenhum dado pode ser
      perdido quando o bucket enche. Então usamos uma área de overflow
      (encadeamento) simples: o que passa de FR vai para essa lista extra.
      O TRATAMENTO/algoritmo formal de colisão e overflow e a CONTAGEM das
      taxas são responsabilidade do EPIC 3 e do EPIC 6 - aqui deixamos apenas
      a estrutura pronta para isso.
    """

    def __init__(self, capacidade):
        self.capacidade = capacidade   # FR
        self.entradas = []             # pares (chave, pagina) dentro do FR
        self.overflow = []             # pares que passaram do FR

    def inserir(self, chave, pagina):
        """Guarda um par (chave, pagina). Se o bucket estiver cheio, usa o overflow."""
        if len(self.entradas) < self.capacidade:
            self.entradas.append((chave, pagina))
        else:
            self.overflow.append((chave, pagina))

    def total(self):
        """Quantos pares esse bucket guarda no total (dentro + overflow)."""
        return len(self.entradas) + len(self.overflow)

    def esta_em_overflow(self):
        """True se esse bucket recebeu mais chaves do que a capacidade FR."""
        return len(self.overflow) > 0


class IndiceHash:
    """
    O índice hash estático inteiro.

    Guarda:
      - nr: número de registros (palavras) que serão indexados.
      - fr: capacidade de cada bucket.
      - nb: número total de buckets.
      - buckets: a lista com os NB buckets.
      - tempo_construcao: quanto tempo levou para construir o índice (HU06/CA14).
    """

    def __init__(self, nr, fr):
        # -------- HU04: cálculo e validação de NB --------
        # Regra RN08: NB tem que ser MAIOR que NR / FR.
        # Usamos NB = (NR // FR) + 1, que é o menor inteiro que satisfaz
        # "NB > NR/FR" em qualquer situação (inclusive quando NR é divisível
        # por FR). Isso também já cumpre o CA10 (impedir NB <= NR/FR).
        if fr <= 0:
            raise ValueError("FR (capacidade do bucket) deve ser maior que zero.")

        self.nr = nr
        self.fr = fr
        self.nb = (nr // fr) + 1

        # Verificação de segurança do CA10.
        if self.nb <= nr / fr:
            raise ValueError("NB inválido: precisa ser maior que NR/FR.")

        # -------- CA09: cria NB buckets de capacidade FR --------
        self.buckets = [Bucket(fr) for _ in range(self.nb)]
        self.tempo_construcao = None

    # -------- HU06: inserção de um registro no índice --------
    def inserir(self, chave, pagina):
        """
        Para uma palavra (chave) e o número da página onde ela está:
          1) aplica a função hash na chave -> descobre o bucket;
          2) guarda no bucket o par (chave, endereço da página).
        """
        endereco_bucket = funcao_hash(chave, self.nb)
        self.buckets[endereco_bucket].inserir(chave, pagina)

    def total_registros_indexados(self):
        """Soma quantos pares estão guardados em todos os buckets."""
        return sum(b.total() for b in self.buckets)

    # -------- Prévia de busca (na verdade é EPIC 4) --------
    # Colocada aqui SÓ para verificarmos que o índice ficou correto.
    def buscar(self, chave):
        """
        Retorna o número da página da palavra usando o índice, ou None.
        (Demonstração/verificação - a funcionalidade completa de busca é o EPIC 4.)
        """
        endereco_bucket = funcao_hash(chave, self.nb)
        bucket = self.buckets[endereco_bucket]
        for (c, pagina) in bucket.entradas:
            if c == chave:
                return pagina
        for (c, pagina) in bucket.overflow:
            if c == chave:
                return pagina
        return None


# ===========================================================================
# HU06 - CONSTRUÇÃO DO ÍNDICE PERCORRENDO AS PÁGINAS
# ===========================================================================
def construir_indice(paginas, fr):
    """
    Constrói o índice hash percorrendo PÁGINA POR PÁGINA (RN12/RN13).

    Passos:
      1) Descobre NR (número de registros) somando as palavras de todas as páginas.
      2) Cria o índice (que já calcula NB e cria os buckets - HU04).
      3) Percorre cada página. O NÚMERO da página é o "endereço" dela.
      4) Para cada palavra da página: aplica a hash e guarda no bucket o par
         (palavra, número da página).
      5) Mede o tempo de construção (CA14 / RNF02).

    Retorna:
      IndiceHash: o índice já preenchido com todos os registros.
    """
    nr = sum(len(pagina) for pagina in paginas)
    indice = IndiceHash(nr, fr)

    inicio = time.perf_counter()
    for numero_pagina, pagina in enumerate(paginas):
        for chave in pagina:
            indice.inserir(chave, numero_pagina)
    fim = time.perf_counter()

    indice.tempo_construcao = fim - inicio
    return indice


# ===========================================================================
# DEMONSTRAÇÃO (para apresentar e testar a parte do EPIC 2)
# ===========================================================================
def _demonstracao():
    """
    Roda o EPIC 2 de ponta a ponta usando o arquivo de palavras:
      - usa o EPIC 1 para carregar e dividir em páginas;
      - constrói o índice (EPIC 2);
      - mostra NB, FR, tempo de construção e alguns buckets de exemplo;
      - confere que TODOS os registros entraram no índice (CA13).
    """
    caminho = os.path.join(_BASE, "Arquivo.Txt", "words.txt")

    # Configuração da equipe:
    tamanho_pagina = 1000   # registros por página (isso é entrada do EPIC 1)
    fr = 100                # FR: capacidade de cada bucket (definido pela equipe - RN09)

    # ---- EPIC 1 (dependência): carregar e paginar ----
    palavras = carregar_palavras(caminho)
    if not palavras:
        print("Não foi possível carregar as palavras. Verifique o arquivo.")
        return
    paginas = dividir_em_paginas(palavras, tamanho_pagina)

    print("=" * 60)
    print(" EPIC 2 - CONSTRUÇÃO DO ÍNDICE HASH ESTÁTICO")
    print("=" * 60)
    print("Total de palavras (NR)....:", len(palavras))
    print("Tamanho da página.........:", tamanho_pagina, "registros")
    print("Total de páginas..........:", len(paginas))
    print("FR (capacidade do bucket).:", fr)
    print()

    # ---- EPIC 2: construir o índice ----
    indice = construir_indice(paginas, fr)

    print("--- HU04: buckets criados ---")
    print("Regra RN08: NB tem que ser > NR/FR =", round(len(palavras) / fr, 2))
    print("NB (número de buckets).....:", indice.nb, "(criados com capacidade FR =", indice.fr, ")")
    print()

    print("--- HU06: índice construído ---")
    print("Tempo de construção........: %.3f segundos" % indice.tempo_construcao)
    print("Registros indexados........:", indice.total_registros_indexados())
    print()

    # ---- Exemplos de bucket (para a interface/EPIC 7 depois ilustrar) ----
    print("--- Exemplo: 3 primeiros pares do bucket 0 ---")
    for (chave, pagina) in indice.buckets[0].entradas[:3]:
        print("   chave = %-20s -> página %d" % (chave, pagina))
    print()

    # ---- HU05: prova de que a hash é determinística e dentro do intervalo ----
    exemplo = palavras[0]
    print("--- HU05: função hash ---")
    print("hash(%r) chamada 3x:" % exemplo,
          funcao_hash(exemplo, indice.nb),
          funcao_hash(exemplo, indice.nb),
          funcao_hash(exemplo, indice.nb),
          "(sempre igual = determinística)")
    print()

    # ---- Verificação final (CA13): índice contém TODOS os registros ----
    print("--- Verificação (CA13) ---")
    if indice.total_registros_indexados() == len(palavras):
        print("OK: o índice contém TODOS os", len(palavras), "registros.")
    else:
        print("ATENÇÃO: número de registros no índice diferente do arquivo!")

    # ---- Prova rápida de que dá para achar palavras pelo índice ----
    achou = indice.buscar(exemplo)
    print("Prévia de busca: a palavra %r está na página %s." % (exemplo, achou))
    print("=" * 60)


if __name__ == "__main__":
    _demonstracao()
