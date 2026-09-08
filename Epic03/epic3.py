# -*- coding: utf-8 -*-
"""
============================================================================
 EPIC 3 - TRATAMENTO DE COLISOES E OVERFLOW
============================================================================

Autor da parte: Isaac Newton
Disciplina: Projeto de Banco de Dados

Este modulo implementa a parte do EPIC 3 do trabalho. Ele e responsavel por
TRATAR as colisoes e o transbordamento (overflow) dos buckets que o EPIC 2
ja sabe criar e povoar.

O EPIC 3 e dividido em 2 historias de usuario:

  HU07 - Resolver colisoes
         (RN14: so conta colisao quando o bucket PRINCIPAL ja esta cheio;
          RN15: a equipe deve implementar um algoritmo de resolucao)

  HU08 - Resolver overflow de buckets
         (RN16: tratar o transbordamento do bucket quando FR e excedido;
          RN17: deve existir um algoritmo de resolucao de overflow)

Algoritmo escolhido pela equipe: ENCADEAMENTO EXTERNO (overflow chaining).
  - Cada bucket tem uma area PRINCIPAL com capacidade FR.
  - Quando a area principal esta cheia e uma nova chave e mapeada para esse
    bucket, isso e uma COLISAO (RN14/CA16).
  - A chave que colidiu e guardada numa area de OVERFLOW encadeada ao
    bucket: um "bucket extra" tambem de capacidade FR, ligado por um
    ponteiro (proximo). Se essa area extra tambem enche, um novo "bucket
    extra" e encadeado, formando uma lista - isso e o "transbordamento em
    cadeia" (HU08).
  - Nenhum registro e perdido (CA15/CA13): toda chave sempre encontra um
    lugar, seja na area principal, seja em algum no da cadeia de overflow.
  - Cada bucket sabe dizer se ELE ENTROU EM OVERFLOW (esta_em_overflow),
    ou seja, se precisou de pelo menos um no extra (CA18).

Observacoes de escopo:
  - CARREGAR o arquivo e DIVIDIR em paginas e o EPIC 1 (feito por outra
    pessoa da equipe).
  - A FUNCAO HASH e a criacao/calculo de NB e o EPIC 2 (feito por outra
    pessoa da equipe).
  - CALCULAR as PORCENTAGENS de colisao e overflow (taxa %) e o EPIC 6.
    Aqui apenas CONTAMOS os eventos (quantidade de colisoes e quantidade de
    buckets em overflow); a taxa percentual e responsabilidade do EPIC 6.
  - BUSCAR usando o indice (tela final de busca) e o EPIC 4. Este modulo
    traz uma busca minima apenas para PROVAR que nenhuma chave se perde
    quando ha colisao/overflow (verificacao), nao e a funcionalidade final.

----------------------------------------------------------------------------
SOBRE OS "MOCKS" (dados/funcoes de outros EPICs ainda nao integrados)
----------------------------------------------------------------------------
Este trabalho e feito em equipe e cada EPIC foi commitado em uma branch
diferente (Epic1, Epic2, ...). Nesta branch (onde o EPIC 3 e o EPIC 6 estao
sendo estruturados) as pastas Epic01/ e Epic02/ dos colegas AINDA NAO FORAM
MESCLADAS. Para o EPIC 3 poder ser desenvolvido, testado e apresentado de
forma independente, este arquivo tenta importar as funcoes reais dos colegas
e, se elas nao estiverem disponiveis, usa uma versao MOCADA (copia fiel do
mesmo algoritmo combinado pela equipe) so para nao travar a execucao.

  -> Quando as branches forem integradas (merge de Epic1/Epic2 -> develop/
     INpart), o bloco de fallback abaixo deixa de ser usado automaticamente
     (o import verdadeiro passa a funcionar) e pode ser removido.
============================================================================
"""

import os
import sys
import time
import random


# ---------------------------------------------------------------------------
# DEPENDENCIA DOS EPICS 1 e 2 (com MOCK/fallback enquanto nao integrados)
# ---------------------------------------------------------------------------
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BASE, "Epic02"))
sys.path.insert(0, os.path.join(_BASE, "Epic01"))

try:
    # Caminho "de verdade": reaproveita tudo que o EPIC 2 ja expoe
    # (que por sua vez ja reaproveita o EPIC 1 internamente).
    from epic2 import carregar_palavras, dividir_em_paginas, funcao_hash
    _USANDO_MOCK = False
except Exception:  # pragma: no cover - EPIC 1/2 ainda nao integrados nesta branch
    _USANDO_MOCK = True

    def carregar_palavras(caminho):
        """MOCK do EPIC 1 (HU01). Mesma assinatura/comportamento combinados."""
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return arquivo.read().splitlines()
        except Exception:
            print("ERRO: nao foi possivel ler o arquivo.")
            return None

    def dividir_em_paginas(palavras, tamanho_pagina):
        """MOCK do EPIC 1 (HU03). Mesma assinatura/comportamento combinados."""
        paginas = []
        for inicio in range(0, len(palavras), tamanho_pagina):
            paginas.append(palavras[inicio:inicio + tamanho_pagina])
        return paginas

    def funcao_hash(chave, nb):
        """
        MOCK do EPIC 2 (HU05). Copia fiel do hash polinomial combinado pela
        equipe (h = h*31 + ord(letra), sempre em [0..NB-1]), so para o
        EPIC 3 conseguir rodar sozinho enquanto o EPIC 2 nao esta mesclado
        nesta branch. Quando integrado, a linha do "try" acima passa a
        importar a funcao REAL do EPIC 2 e este mock nem chega a ser usado.
        """
        h = 0
        for letra in chave:
            h = (h * 31 + ord(letra)) % nb
        return h


def _gerar_dados_mock(quantidade=2000, tamanho_pagina=100, semente=42):
    """
    Gera uma massa de dados MOCADA para quando o arquivo real de palavras
    (EPIC 1) nao estiver acessivel nesta branch. Usada apenas como ultimo
    recurso na demonstracao, para o EPIC 3 nunca ficar sem ter o que
    mostrar. Palavras sinteticas, mas deterministicas (mesma semente).
    """
    rng = random.Random(semente)
    alfabeto = "abcdefghijklmnopqrstuvwxyz"
    palavras = []
    for i in range(quantidade):
        tamanho = rng.randint(3, 10)
        palavra = "".join(rng.choice(alfabeto) for _ in range(tamanho)) + str(i)
        palavras.append(palavra)
    return dividir_em_paginas(palavras, tamanho_pagina)


# ===========================================================================
# HU07 + HU08 - ESTRUTURA COM COLISAO E OVERFLOW ENCADEADO
# ===========================================================================
class NoOverflow:
    """
    Um "no" (bucket extra) da cadeia de overflow. Cada no tem a MESMA
    capacidade FR do bucket principal e um ponteiro para o proximo no,
    formando uma lista encadeada quando o overflow tambem enche (HU08).
    """

    def __init__(self, capacidade):
        self.capacidade = capacidade
        self.entradas = []      # pares (chave, pagina) guardados neste no
        self.proximo = None     # proximo NoOverflow encadeado, ou None

    def esta_cheio(self):
        return len(self.entradas) >= self.capacidade


class BucketComColisao:
    """
    Bucket do indice ja preparado para tratar colisao e overflow.

    - capacidade (FR): quantas chaves cabem na area PRINCIPAL.
    - entradas: pares (chave, pagina) que couberam na area principal.
    - overflow: cabeca da lista encadeada de NoOverflow (None se o bucket
      nunca precisou de overflow).
    - colisoes: quantas chaves DESTE bucket precisaram ir para o overflow
      (RN14 - so conta quando a area principal ja estava cheia).
    """

    def __init__(self, capacidade):
        self.capacidade = capacidade
        self.entradas = []
        self.overflow = None
        self.colisoes = 0

    def esta_cheio(self):
        """A area PRINCIPAL do bucket esta cheia (vai gerar colisao)?"""
        return len(self.entradas) >= self.capacidade

    def esta_em_overflow(self):
        """Este bucket ja precisou de algum no de overflow? (CA18)"""
        return self.overflow is not None

    def inserir(self, chave, pagina):
        """
        Insere (chave, pagina) no bucket, tratando colisao/overflow.

        Passo a passo:
          1) Se ainda ha espaco na area PRINCIPAL, guarda ali (sem colisao).
          2) Se a area principal esta cheia (RN14) -> e uma COLISAO. A
             chave precisa ser resolvida via a cadeia de overflow (HU07).
          3) Percorre a cadeia de overflow procurando um no com espaco.
             Se nenhum no tiver espaco (ou a cadeia ainda nao existir),
             cria-se um NOVO no de overflow encadeado ao final da lista
             (HU08 - o bucket "transborda" e ganha mais um no).

        Retorna uma string indicando o que aconteceu, util para estatistica
        e para a interface grafica (EPIC 7) destacar o que ocorreu.
        """
        if not self.esta_cheio():
            self.entradas.append((chave, pagina))
            return "inserido_direto"

        # --- RN14: bucket principal cheio -> e uma colisao ---
        self.colisoes += 1

        no_atual = self.overflow
        no_anterior = None
        while no_atual is not None and no_atual.esta_cheio():
            no_anterior = no_atual
            no_atual = no_atual.proximo

        if no_atual is None:
            # Nenhum no com espaco (ou a cadeia nao existia): cria um novo.
            novo_no = NoOverflow(self.capacidade)
            if no_anterior is None:
                self.overflow = novo_no          # 1o no de overflow do bucket
            else:
                no_anterior.proximo = novo_no    # encadeia mais um no
            no_atual = novo_no

        no_atual.entradas.append((chave, pagina))
        return "colisao_resolvida_por_overflow"

    def buscar(self, chave):
        """Procura a chave na area principal e depois na cadeia de overflow."""
        for (c, pagina) in self.entradas:
            if c == chave:
                return pagina
        no = self.overflow
        while no is not None:
            for (c, pagina) in no.entradas:
                if c == chave:
                    return pagina
            no = no.proximo
        return None

    def total_registros(self):
        """Quantas chaves este bucket guarda no total (principal + overflow)."""
        total = len(self.entradas)
        no = self.overflow
        while no is not None:
            total += len(no.entradas)
            no = no.proximo
        return total

    def total_nos_overflow(self):
        """Quantos nos de overflow foram encadeados neste bucket."""
        total = 0
        no = self.overflow
        while no is not None:
            total += 1
            no = no.proximo
        return total


class IndiceComColisao:
    """
    Indice hash estatico completo, ja com o tratamento de colisao e
    overflow do EPIC 3. Mantem os contadores exigidos pelas regras
    RN08/RN14/RN16, que o EPIC 6 vai usar para calcular as taxas (%).
    """

    def __init__(self, nr, fr):
        if fr <= 0:
            raise ValueError("FR (capacidade do bucket) deve ser maior que zero.")

        self.nr = nr
        self.fr = fr
        # Regra RN08: NB > NR/FR. Usamos (NR // FR) + 1, o menor inteiro
        # que sempre satisfaz a regra (mesma formula usada no EPIC 2).
        self.nb = (nr // fr) + 1
        if self.nb <= nr / fr:
            raise ValueError("NB invalido: precisa ser maior que NR/FR.")

        self.buckets = [BucketComColisao(fr) for _ in range(self.nb)]
        self.tempo_construcao = None

    def inserir(self, chave, pagina):
        endereco = funcao_hash(chave, self.nb)
        return self.buckets[endereco].inserir(chave, pagina)

    def buscar(self, chave):
        endereco = funcao_hash(chave, self.nb)
        return self.buckets[endereco].buscar(chave)

    # -------- HU07: estatistica de colisoes (contagem, nao a taxa %) --------
    def total_colisoes(self):
        """
        Soma de colisoes de todos os buckets (RN14/CA16). Representa quantas
        chaves precisaram ser resolvidas via overflow porque o bucket em que
        caíram ja estava cheio.
        """
        return sum(b.colisoes for b in self.buckets)

    # -------- HU08: estatistica de overflow (contagem, nao a taxa %) --------
    def total_buckets_em_overflow(self):
        """Quantos buckets (dentre os NB) precisaram de overflow (CA18)."""
        return sum(1 for b in self.buckets if b.esta_em_overflow())

    def total_nos_overflow(self):
        """Quantos 'blocos' extras de overflow foram criados no total."""
        return sum(b.total_nos_overflow() for b in self.buckets)

    def total_registros_indexados(self):
        """Confirma que nenhum registro foi perdido (CA15/CA13)."""
        return sum(b.total_registros() for b in self.buckets)


# ===========================================================================
# HU06/HU07/HU08 - CONSTRUCAO DO INDICE JA TRATANDO COLISAO/OVERFLOW
# ===========================================================================
def construir_indice_com_colisoes(paginas, fr):
    """
    Constroi o indice percorrendo pagina por pagina (igual ao EPIC 2), mas
    usando o BucketComColisao (EPIC 3), que ja resolve colisao (HU07) e
    overflow (HU08) durante a propria insercao.
    """
    nr = sum(len(pagina) for pagina in paginas)
    indice = IndiceComColisao(nr, fr)

    inicio = time.perf_counter()
    for numero_pagina, pagina in enumerate(paginas):
        for chave in pagina:
            indice.inserir(chave, numero_pagina)
    fim = time.perf_counter()

    indice.tempo_construcao = fim - inicio
    return indice


# ===========================================================================
# DEMONSTRACAO (para apresentar e testar a parte do EPIC 3)
# ===========================================================================
def _demonstracao():
    """
    Roda o EPIC 3 de ponta a ponta:
      - carrega e pagina as palavras (EPIC 1, real ou mocado);
      - constroi o indice ja tratando colisao/overflow (EPIC 3);
      - mostra quantas colisoes e quantos buckets em overflow ocorreram;
      - confere que NENHUM registro foi perdido (CA15/CA13).

    Um FR pequeno e usado de proposito na demonstracao para FORCAR a
    ocorrencia de colisoes e overflow e deixar visivel que o algoritmo
    funciona (com FR grande, quase nao haveria colisao para mostrar).
    """
    caminho = os.path.join(_BASE, "Arquivo.Txt", "words.txt")
    tamanho_pagina = 1000
    fr = 20  # FR pequeno de proposito, so na demo, para EVIDENCIAR colisao/overflow

    print("=" * 70)
    print(" EPIC 3 - TRATAMENTO DE COLISOES E OVERFLOW")
    print("=" * 70)
    if _USANDO_MOCK:
        print("[AVISO] EPIC 1/EPIC 2 ainda nao integrados nesta branch.")
        print("        Usando funcoes MOCADAS (mesmo algoritmo combinado)")
        print("        ate o merge das branches Epic1/Epic2 acontecer.")
        print()

    palavras = carregar_palavras(caminho)
    if palavras:
        paginas = dividir_em_paginas(palavras, tamanho_pagina)
    else:
        print("[AVISO] Arquivo de palavras nao encontrado em:", caminho)
        print("        Gerando massa de dados MOCADA apenas para a demo.")
        paginas = _gerar_dados_mock()

    nr = sum(len(p) for p in paginas)
    print("Total de registros (NR)....:", nr)
    print("Tamanho da pagina...........:", tamanho_pagina)
    print("Total de paginas.............:", len(paginas))
    print("FR (capacidade do bucket)....:", fr, "  <- pequeno de proposito na demo")
    print()

    indice = construir_indice_com_colisoes(paginas, fr)

    print("--- HU04/EPIC2 (reaproveitado): buckets ---")
    print("NB (numero de buckets)......:", indice.nb)
    print()

    print("--- HU07: colisoes ---")
    print("Total de colisoes............:", indice.total_colisoes())
    print()

    print("--- HU08: overflow ---")
    print("Buckets que entraram em overflow:", indice.total_buckets_em_overflow(),
          "de", indice.nb)
    print("Total de nos de overflow criados:", indice.total_nos_overflow())
    print()

    print("--- Verificacao (CA13/CA15): nenhum registro perdido ---")
    total_indexado = indice.total_registros_indexados()
    if total_indexado == nr:
        print("OK: os", nr, "registros estao todos no indice",
              "(mesmo com colisao/overflow, nada foi perdido).")
    else:
        print("ATENCAO: esperado", nr, "registros, mas o indice tem", total_indexado)
    print()

    print("Tempo de construcao..........: %.3f segundos" % indice.tempo_construcao)

    # ---- Exemplo de um bucket que sofreu colisao/overflow, se houver ----
    for i, bucket in enumerate(indice.buckets):
        if bucket.esta_em_overflow():
            print()
            print("--- Exemplo: bucket %d entrou em overflow ---" % i)
            print("Entradas na area principal (FR=%d):" % fr, len(bucket.entradas))
            print("Colisoes neste bucket:", bucket.colisoes)
            print("Numero de nos de overflow encadeados:", bucket.total_nos_overflow())
            break
    print("=" * 70)


if __name__ == "__main__":
    _demonstracao()
