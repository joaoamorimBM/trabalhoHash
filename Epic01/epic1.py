def carregar_palavras(caminho):
    try:
        with open(caminho, "r") as arquivo:
            palavras = arquivo.read().splitlines()
    except Exception:
        print("ERRO: não foi possível ler o arquivo.")
        return None
    return palavras


def solicitar_tamanho_pagina():
    try:
        tamanho = int(input("Digite o tamanho da página (registros por página): "))
    except ValueError:
        print("ERRO: você deve digitar um número inteiro.")
        return None
    if tamanho <= 0:
        print("ERRO: o tamanho da página deve ser maior que zero.")
        return None
    return tamanho


def dividir_em_paginas(palavras, tamanho_pagina):
    quantidade = (len(palavras) + tamanho_pagina - 1) // tamanho_pagina
    paginas = [[] for _ in range(quantidade)]
    for indice, palavra in enumerate(palavras):
        paginas[indice // tamanho_pagina].append(palavra)
    return paginas


def mostrar_pagina(paginas, numero):
    pagina = paginas[numero]
    print("Numero da pagina:", numero)
    print("Quantidade de registros:", len(pagina))
    print("Primeiros 5 registros:", pagina[:5])
    print()


def main():
    caminho = "../Arquivo.Txt/words.txt"

    palavras = carregar_palavras(caminho)
    if palavras is None:
        return

    if len(palavras) == 0:
        print("ERRO: o arquivo está vazio.")
        return

    tamanho_pagina = solicitar_tamanho_pagina()
    if tamanho_pagina is None:
        return

    paginas = dividir_em_paginas(palavras, tamanho_pagina)

    print("Total de palavras carregadas:", len(palavras))
    print("Tamanho da pagina:", tamanho_pagina, "palavras")
    print("Total de paginas:", len(paginas))
    print()

    print("===== PRIMEIRA PAGINA =====")
    mostrar_pagina(paginas, 0)

    print("===== ULTIMA PAGINA =====")
    mostrar_pagina(paginas, len(paginas) - 1)


if __name__ == "__main__":
    main()