# EPIC 2 — Construção do Índice Hash Estático

Parte do trabalho: **Vinicius Andrade**

Esta pasta implementa o **EPIC 2** do projeto: a construção do índice hash
estático em cima das páginas geradas pelo EPIC 1.

## O que este EPIC entrega

| História | O que faz | Onde está no código |
|----------|-----------|---------------------|
| **HU04** | Cria os buckets: calcula **NB** (NB > NR/FR), usa a capacidade **FR** e cria os NB buckets. | classe `IndiceHash.__init__` |
| **HU05** | Função hash **própria** (sem usar o `hash()` da linguagem), determinística e sempre em `[0..NB-1]`. | função `funcao_hash` |
| **HU06** | Constrói o índice percorrendo **página por página** e guardando `(chave → nº da página)`. Mede o tempo. | função `construir_indice` |

## Conceitos rápidos

- **NR** = número de registros (palavras). Aqui: 466.550.
- **FR** = capacidade do bucket (quantas chaves cabem). Definido pela equipe: **100**.
- **NB** = número de buckets. Regra RN08: `NB > NR/FR`. Usamos `NB = (NR // FR) + 1`,
  o menor inteiro que sempre satisfaz a regra. Aqui: **4666**.
- **Função hash**: hash polinomial `h = (h * 31 + ord(letra)) % NB`. O `% NB`
  garante o intervalo válido; a conta fixa garante o determinismo.
- **Overflow**: quando um bucket passa de FR, o excedente vai para uma área
  de overflow (para não perder nenhum registro — CA13). O **tratamento formal**
  e a **contagem das taxas** de colisão/overflow são do EPIC 3 e do EPIC 6.

## Como rodar

```bash
cd Epic02
python3 epic2.py
```

Saída esperada (resumo): NR = 466550, NB = 4666, FR = 100, tempo de construção
~1s e a confirmação de que os 466.550 registros entraram no índice.

## Dependência

Reusa `carregar_palavras` e `dividir_em_paginas` do **EPIC 1**
(`Epic01/epic1.py`). Se o arquivo do EPIC 1 não estiver acessível, o módulo tem
uma versão mínima de emergência só para conseguir rodar sozinho.
