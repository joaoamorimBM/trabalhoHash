const API_URL = 'http://127.0.0.1:8000';

export async function fetchLoadData(pageSize) {
  const response = await fetch(`${API_URL}/load-data`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pageSize })
  });
  if (!response.ok) throw new Error('Erro ao carregar dados do arquivo.');
  return await response.json();
}

export async function fetchBuildIndex(bucketCapacity) {
  const response = await fetch(`${API_URL}/build-index`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ bucketCapacity })
  });
  if (!response.ok) throw new Error('Erro ao construir o índice hash.');
  return await response.json();
}

export async function fetchSearch(key) {
  const response = await fetch(`${API_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key })
  });
  if (!response.ok) throw new Error('Erro ao realizar a busca.');
  return await response.json();
}