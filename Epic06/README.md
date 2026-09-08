# EPIC 6 — Estatísticas e Métricas

Parte do trabalho: **Isaac Newton**

Esta pasta implementa o **EPIC 6** do projeto: o cálculo das taxas
percentuais de colisão e de overflow do índice hash estático, a partir das
contagens que o EPIC 3 já produz.

## O que este EPIC entrega

| História | O que faz | Onde está no código |
|----------|-----------|----------------------|
| **HU12** | Calcula e exibe a **taxa de colisões (%)** (RN24/CA25). | `taxa_de_colisoes` |
| **HU13** | Calcula e exibe a **taxa de overflow (%)** (RN25/CA26). | `taxa_de_overflow` |

## Fórmulas usadas pela equipe

```
taxa_de_colisoes (%) = (total de colisões / NR) x 100
taxa_de_overflow (%) = (buckets em overflow / NB) x 100
```

- **NR** = número total de registros (chaves) inseridos no índice.
- **NB** = número total de buckets do índice.
- Uma **colisão** é cada chave que precisou ir para a área de overflow
  porque a área principal do bucket já estava cheia (ver EPIC 3, RN14).
- Um bucket **"entra em overflow"** quando precisa de pelo menos um nó
  extra encadeado (ver EPIC 3, HU08).

`calcular_estatisticas(indice)` reúne NR, NB, FR, as duas contagens e as
duas taxas num único dicionário — pensado para a interface gráfica do
EPIC 7 só precisar chamar essa função e exibir os campos.

## Como rodar

```bash
cd Epic06
python3 epic6.py
```

A demonstração constrói o índice para três valores de FR (10, 20 e 50) e
mostra como a taxa de colisão/overflow muda conforme FR/NB são
dimensionados — quanto menor o FR (para o mesmo NR), maior tende a ser a
taxa de colisão e de overflow (RN08/RN09). Com o arquivo completo
(466.550 palavras) as três construções juntas levam poucos segundos.

## Dependência e MOCKS

O EPIC 6 depende do **EPIC 3** (`construir_indice_com_colisoes`, que por sua
vez já reaproveita os EPICs 1 e 2 internamente) para ter um índice com as
contagens de colisão e overflow prontas.

Como a branch `Epic3` ainda não foi mesclada nesta branch, o arquivo
`epic6.py` tenta importar a construção do índice do EPIC 3 e, se não
conseguir, usa uma versão **MOCADA** — mesma fórmula, mesmo algoritmo de
overflow em cadeia — só para o EPIC 6 poder ser testado e apresentado de
forma independente.

Assim que as branches forem integradas, o import real passa a funcionar
sozinho e o bloco de mock pode ser removido.
