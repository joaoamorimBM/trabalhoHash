import time


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
    paginas = []
    for inicio in range(0, len(palavras), tamanho_pagina):
        pagina = palavras[inicio : inicio + tamanho_pagina]
        paginas.append(pagina)
    return paginas


def solicitar_chave():
    chave = input("Digite a chave de busca: ")
    return chave


def table_scan(paginas, chave):
    total = len(paginas)
    for numero, pagina in enumerate(paginas):
        if total <= 20 or numero < 5 or numero > total - 5 or chave in pagina:
            print("  Página {}: {} registros — primeiros 5: {}".format(
                numero, len(pagina), pagina[:5]))
        elif numero == 5:
            print("  ... [páginas intermediárias omitidas] ...")
        if chave in pagina:
            return numero
    return None


def funcao_hash(chave, nb):
    h = 0
    for letra in chave:
        h = (h * 31 + ord(letra)) % nb
    return h


class Bucket:
    def __init__(self, capacidade):
        self.capacidade = capacidade
        self.entradas = []
        self.overflow = []

    def inserir(self, chave, pagina):
        if len(self.entradas) < self.capacidade:
            self.entradas.append((chave, pagina))
        else:
            self.overflow.append((chave, pagina))

    def total(self):
        return len(self.entradas) + len(self.overflow)


class IndiceHash:
    def __init__(self, nr, fr):
        if fr <= 0:
            raise ValueError("FR (capacidade do bucket) deve ser maior que zero.")
        self.nr = nr
        self.fr = fr
        self.nb = (nr // fr) + 1
        if self.nb <= nr / fr:
            raise ValueError("NB inválido: precisa ser maior que NR/FR.")
        self.buckets = [Bucket(fr) for _ in range(self.nb)]
        self.tempo_construcao = None

    def inserir(self, chave, pagina):
        endereco_bucket = funcao_hash(chave, self.nb)
        self.buckets[endereco_bucket].inserir(chave, pagina)

    def buscar(self, chave):
        endereco_bucket = funcao_hash(chave, self.nb)
        bucket = self.buckets[endereco_bucket]
        for (c, pagina) in bucket.entradas:
            if c == chave:
                return pagina
        for (c, pagina) in bucket.overflow:
            if c == chave:
                return pagina
        return None


def construir_indice(paginas, fr):
    nr = sum(len(pagina) for pagina in paginas)
    indice = IndiceHash(nr, fr)
    inicio = time.perf_counter()
    for numero_pagina, pagina in enumerate(paginas):
        for chave in pagina:
            indice.inserir(chave, numero_pagina)
    fim = time.perf_counter()
    indice.tempo_construcao = fim - inicio
    return indice


def main():
    caminho = "../Arquivo.Txt/words.txt"

    palavras = carregar_palavras(caminho)
    if palavras is None or len(palavras) == 0:
        print("ERRO: não foi possível carregar o arquivo ou ele está vazio.")
        return

    tamanho_pagina = solicitar_tamanho_pagina()
    if tamanho_pagina is None:
        return

    fr = 10

    paginas = dividir_em_paginas(palavras, tamanho_pagina)

    chave = solicitar_chave()

    print()
    print("########## TABLE SCAN ##########")
    inicio_scan = time.perf_counter()
    pagina_encontrada = table_scan(paginas, chave)
    fim_scan = time.perf_counter()
    tempo_scan = fim_scan - inicio_scan

    if pagina_encontrada is None:
        custo_scan = len(paginas)
        print("Chave '{}' NAO encontrada no table scan.".format(chave))
        print("Custo do table scan: {} página(s) lida(s).".format(custo_scan))
    else:
        custo_scan = pagina_encontrada + 1
        print()
        print("Chave '{}' encontrada na página {}.".format(chave, pagina_encontrada))
        print("Custo do table scan: {} página(s) lida(s).".format(custo_scan))
        print("Registros da página encontrada:", paginas[pagina_encontrada])
    print("Tempo do table scan: {:.6f} segundos".format(tempo_scan))

    print()
    print("########## BUSCA POR ÍNDICE ##########")
    indice = construir_indice(paginas, fr)
    inicio_indice = time.perf_counter()
    pagina_no_indice = indice.buscar(chave)
    fim_indice = time.perf_counter()
    tempo_indice = fim_indice - inicio_indice

    custo_indice = 1
    if pagina_no_indice is None:
        print("Chave '{}' NAO encontrada no índice.".format(chave))
        print("Custo da busca por índice: {} bucket(s) lido(s).".format(custo_indice))
    else:
        print("Chave '{}' encontrada na página {}.".format(chave, pagina_no_indice))
        print("Custo da busca por índice: {} página(s) lida(s).".format(custo_indice))
    print("Tempo da busca por índice: {:.6f} segundos".format(tempo_indice))

    print()
    print("########## COMPARAÇÃO ##########")
    print("Tempo do table scan...........: {:.6f} s".format(tempo_scan))
    print("Tempo da busca por índice.....: {:.6f} s".format(tempo_indice))
    if tempo_indice > 0:
        percentual = (tempo_scan - tempo_indice) / tempo_indice * 100
        print("Diferença percentual de tempo.: {:.2f}%".format(percentual))

    print("Custo do table scan...........: {} páginas lidas".format(custo_scan))
    print("Custo da busca por índice.....: {} página(s) lida(s)".format(custo_indice))
    if custo_scan > 0:
        reducao = (custo_scan - custo_indice) / custo_scan * 100
        print("Redução percentual de custo...: {:.2f}%".format(reducao))


if __name__ == "__main__":
    main()