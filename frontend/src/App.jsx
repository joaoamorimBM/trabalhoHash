import { useState } from 'react'
import { mockData } from './mockData';
import './App.css'

export default function App() {
  // Configurações
  const [pageSize, setPageSize] = useState(1000);
  const [bucketCapacity, setBucketCapacity] = useState(10);
  const [searchKey, setSearchKey] = useState('');

  // Estados dos Dados
  const [loadedData, setLoadedData] = useState(null);
  const [indexData, setIndexData] = useState(null);
  const [searchResult, setSearchResult] = useState(null);

  // Simulações de chamadas para o Back-end
  const handleLoadData = () => {
    setLoadedData(mockData.loadData);
  };

  const handleBuildIndex = () => {
    setIndexData(mockData.buildIndex);
  };

  const handleSearchIndex = () => {
    setSearchResult({
      index: mockData.searchIndexResult,
      scan: mockData.searchScanResult
    });
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1000px', margin: '0 auto' }}>
      <h1>Índice Hash Estático — Painel de Controle</h1>

      {/* 1. CONFIGURAÇÃO E CARGA */}
      <section style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2>1. Carga de Dados e Parâmetros</h2>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label>
            Tamanho da Página (registros):
            <input 
              type="number" 
              value={pageSize} 
              onChange={(e) => setPageSize(Number(e.target.value))}
              style={{ marginLeft: '8px', padding: '4px' }}
            />
          </label>
          <label>
            Capacidade do Bucket (FR):
            <input 
              type="number" 
              value={bucketCapacity} 
              onChange={(e) => setBucketCapacity(Number(e.target.value))}
              style={{ marginLeft: '8px', padding: '4px' }}
            />
          </label>
          <button onClick={handleLoadData} style={{ padding: '6px 12px', cursor: 'pointer' }}>Carregar Arquivo</button>
          <button onClick={handleBuildIndex} disabled={!loadedData} style={{ padding: '6px 12px', cursor: 'pointer' }}>Construir Índice</button>
        </div>
      </section>

      {/* 2. VISUALIZAÇÃO DAS PÁGINAS (PRIMEIRA E ÚLTIMA) */}
      {loadedData && (
        <section style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
          <h2>2. Estrutura de Páginas ({loadedData.totalWords.toLocaleString()} palavras em {loadedData.totalPages} páginas)</h2>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1, background: '#f9f9f9', padding: '10px', borderRadius: '4px' }}>
              <h3>Primeira Página (Página #{loadedData.firstPage.pageNumber})</h3>
              <ul>
                {loadedData.firstPage.records.map((word, i) => <li key={i}>{word}</li>)}
              </ul>
            </div>
            <div style={{ flex: 1, background: '#f9f9f9', padding: '10px', borderRadius: '4px' }}>
              <h3>Última Página (Página #{loadedData.lastPage.pageNumber})</h3>
              <ul>
                {loadedData.lastPage.records.map((word, i) => <li key={i}>{word}</li>)}
              </ul>
            </div>
          </div>
        </section>
      )}

      {/* 3. MÉTRICAS E ESTATÍSTICAS DO HASH */}
      {indexData && (
        <section style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', marginBottom: '20px', background: '#eef6ff' }}>
          <h2>3. Estatísticas do Índice Hash</h2>
          <p><strong>Total de Buckets (NB):</strong> {indexData.totalBuckets}</p>
          <p><strong>Tempo de Construção:</strong> {indexData.buildTimeMs} ms</p>
          <p><strong>Taxa de Colisões:</strong> {indexData.collisionRate}%</p>
          <p><strong>Taxa de Overflow:</strong> {indexData.overflowRate}%</p>
        </section>
      )}

      {/* 4. BUSCA E DESTAQUE VISUAL */}
      {indexData && (
        <section style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
          <h2>4. Pesquisa de Chave</h2>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
            <input 
              type="text" 
              placeholder="Digite a palavra de busca..." 
              value={searchKey} 
              onChange={(e) => setSearchKey(e.target.value)}
              style={{ flex: 1, padding: '8px' }}
            />
            <button onClick={handleSearchIndex} style={{ padding: '8px 16px', cursor: 'pointer' }}>Buscar</button>
          </div>

          {searchResult && (
            <div>
              <h3>Resultado da Comparação:</h3>
              <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#eee' }}>
                    <th>Métrica</th>
                    <th>Busca por Índice</th>
                    <th>Table Scan</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Status</td>
                    <td>{searchResult.index.found ? 'Encontrada' : 'Não Encontrada'}</td>
                    <td>{searchResult.scan.found ? 'Encontrada' : 'Não Encontrada'}</td>
                  </tr>
                  <tr>
                    <td>Página Encontrada</td>
                    <td>Página #{searchResult.index.pageNumber}</td>
                    <td>Página #{searchResult.scan.pageNumber}</td>
                  </tr>
                  <tr>
                    <td>Custo (Acessos a Disco)</td>
                    <td>{searchResult.index.costPagesRead} leitura(s)</td>
                    <td>{searchResult.scan.costPagesRead} leitura(s)</td>
                  </tr>
                  <tr>
                    <td>Tempo de Execução</td>
                    <td>{searchResult.index.timeMs} ms</td>
                    <td>{searchResult.scan.timeMs} ms</td>
                  </tr>
                </tbody>
              </table>

              {/* DESTAQUE VISUAL (CA29) */}
              <div style={{ marginTop: '15px', padding: '10px', background: '#e2f0d9', border: '1px solid #70ad47', borderRadius: '4px' }}>
                <strong>Destaque Visual de Acesso:</strong> 
                <br />
                Bucket Acessado: <code>#{searchResult.index.bucketIndex}</code> | Página Acessada: <code>#{searchResult.index.pageNumber}</code>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}