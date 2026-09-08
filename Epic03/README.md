# EPIC 3 — Tratamento de Colisões e Overflow

Parte do trabalho: **Isaac Newton**

Esta pasta implementa o **EPIC 3** do projeto: o tratamento de colisões e do
transbordamento (overflow) dos buckets do índice hash estático construído no
EPIC 2.

## O que este EPIC entrega

| História | O que faz | Onde está no código |
|----------|-----------|----------------------|
| **HU07** | Resolve colisões: só conta colisão quando a área principal do bucket (capacidade FR) já está cheia (RN14) e resolve com um algoritmo de encadeamento (RN15). | `BucketComColisao.inserir` |
| **HU08** | Resolve overflow: quando a área de overflow também enche, encadeia um novo "nó" de overflow (RN16/RN17). | `NoOverflow`, `BucketComColisao.inserir` |

## Algoritmo escolhido: encadeamento externo (overflow chaining)

- Cada bucket tem uma área **principal** com capacidade **FR**.
- Quando essa área está cheia e uma nova chave é mapeada para o bucket, é
  uma **colisão** (RN14/CA16) — só conta como colisão a partir daí, chaves
  que ainda cabem na área principal não são colisão.
- A chave que colidiu vai para uma área de **overflow** encadeada ao
  bucket: um "bucket extra", também de capacidade FR, ligado por um
  ponteiro. Se esse extra também enche, um novo nó é encadeado — isso é o
  **transbordamento em cadeia** (HU08/CA17).
- Nenhum registro é perdido (CA13/CA15): toda chave sempre encontra um
  lugar, seja na área principal, seja em algum nó da cadeia de overflow.

## Estatísticas expostas (usadas pelo EPIC 6)

- `indice.total_colisoes()` — quantidade de colisões (RN14/CA16).
- `indice.total_buckets_em_overflow()` — quantos buckets, dentre os NB,
  precisaram de overflow (CA18).
- `indice.total_registros_indexados()` — confere que nada foi perdido.

O **cálculo da taxa percentual** (colisões/overflow em %) é responsabilidade
do **EPIC 6**, que consome essas contagens.

## Como rodar

```bash
cd Epic03
python3 epic3.py
```

A demonstração usa um **FR pequeno de propósito** (FR = 20) para forçar a
ocorrência de colisões/overflow e deixar visível que o algoritmo funciona.
Com o arquivo completo (466.550 palavras) a construção do índice leva menos
de 1 segundo.

## Dependência e MOCKS

O EPIC 3 depende de:

- **EPIC 1** (`carregar_palavras`, `dividir_em_paginas`) — carga e paginação.
- **EPIC 2** (`funcao_hash`) — função hash própria da equipe.

Como as branches `Epic1` e `Epic2` ainda não foram mescladas nesta branch, o
arquivo `epic3.py` tenta importar essas funções do módulo real do EPIC 2
(que já reaproveita o EPIC 1 internamente) e, se não conseguir, usa uma
versão **MOCADA** — cópia fiel do mesmo algoritmo combinado pela equipe
(mesmo hash polinomial, mesma leitura/paginação) — só para o EPIC 3 poder
ser desenvolvido, testado e apresentado de forma independente.

Assim que as branches forem integradas (merge de `Epic1`/`Epic2` para
`develop`/`INpart`), o import real passa a funcionar sozinho — nenhuma
alteração de código é necessária, e o bloco de mock pode ser removido.
