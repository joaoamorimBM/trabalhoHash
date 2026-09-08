import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa as funções com os nomes exatos do epic1.py
from Epic01.epic1 import carregar_palavras, dividir_em_paginas

app = FastAPI(title="API Índice Hash Estático")

# Libera o acesso para o React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/load-data")
def route_load_data(params: dict):
    page_size = params.get("pageSize", 1000)
    
    # 1. Carrega as palavras do arquivo txt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Arquivo.Txt", "words.txt")

    palavras = carregar_palavras(file_path)
    if not palavras:
        alt_path = os.path.join(base_dir, "words.txt")
        palavras = carregar_palavras(alt_path)

    if not palavras:
        return {"error": "Não foi possível carregar o arquivo"}

    # 2. Divide em páginas usando a função do epic1.py
    paginas = dividir_em_paginas(palavras, page_size)
    
    # 3. Retorna a estrutura esperada pelo React
    return {
        "totalWords": len(palavras),
        "totalPages": len(paginas),
        "pageSize": page_size,
        "firstPage": {
            "pageNumber": 1,
            "records": paginas[0][:5] if paginas else []
        },
        "lastPage": {
            "pageNumber": len(paginas),
            "records": paginas[-1][:5] if paginas else []
        }
    }

@app.post("/build-index")
def route_build_index(params: dict):
    # Endpoint temporário até conectar com o Epic 2/3 do grupo
    bucket_capacity = params.get("bucketCapacity", 10)
    return {
        "totalBuckets": 50000,
        "bucketCapacity": bucket_capacity,
        "buildTimeMs": 120.0,
        "collisionRate": 10.0,
        "overflowRate": 2.0
    }

@app.post("/search")
def route_search(params: dict):
    # Endpoint temporário até conectar com o Epic 4 do grupo
    key = params.get("key", "")
    return {
        "index": {
            "found": True,
            "key": key,
            "pageNumber": 1,
            "bucketIndex": 2,
            "costPagesRead": 1,
            "timeMs": 0.15
        },
        "scan": {
            "found": True,
            "key": key,
            "pageNumber": 1,
            "costPagesRead": 1,
            "timeMs": 4.5
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)