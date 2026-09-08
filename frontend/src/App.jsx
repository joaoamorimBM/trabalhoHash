import { useState } from 'react'
import { mockData } from './mockData';
import './App.css';
import { fetchLoadData, fetchBuildIndex, fetchSearch } from './services/api';

export default function App() {
  // Configurações
  const [pageSize, setPageSize] = useState(1000);
  const [bucketCapacity, setBucketCapacity] = useState(10);
  const [searchKey, setSearchKey] = useState('');

  // Estados dos Dados
  const [loadedData, setLoadedData] = useState(null);
  const [indexData, setIndexData] = useState(null);
  const [searchResult, setSearchResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const handleLoadData = async () => {
    setLoading(true);
    try {
      const data = await fetchLoadData(pageSize);
      setLoadedData(data);
    } catch (err) {
      console.warn("Servidor Python offline, carregando mockData...", err);
      setLoadedData(mockData.loadData);
    } finally {
      setLoading(false);
    }
  };

const handleBuildIndex = async () => {
    setLoading(true);
    try {
      const data = await fetchBuildIndex(bucketCapacity);
      setIndexData(data);
    } catch (err) {
      console.warn("Servidor Python offline, carregando mockData...", err);
      setIndexData(mockData.buildIndex);
    } finally {
      setLoading(false);
    }
  };

const handleSearchIndex = async () => {
    setLoading(true);
    try {
      const data = await fetchSearch(searchKey);
      setSearchResult(data);
    } catch (err) {
      console.warn("Servidor Python offline, carregando mockData...", err);
      setSearchResult({
        index: mockData.searchIndexResult,
        scan: mockData.searchScanResult
      });
    } finally {
      setLoading(false);
    }
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

          {/* 3. BOTÕES ATUALIZADOS COM ESTADO E FEEDBACK VISUAL DE LOADING */}
          <button 
            onClick={handleLoadData} 
            disabled={loading}
            style={{ padding: '6px 12px', cursor: loading ? 'not-allowed' : 'pointer' }}
          >
            {loading ? 'Carregando...' : 'Carregar Arquivo'}
          </button>

          <button 
            onClick={handleBuildIndex} 
            disabled={!loadedData || loading}
            style={{ padding: '6px 12px', cursor: (loading || !loadedData) ? 'not-allowed' : 'pointer' }}
          >
            {loading ? 'Construindo...' : 'Construir Índice'}
          </button>
        </div>
      </section>

      {/* 2. VISUALIZAÇÃO DAS PÁGINAS (PRIMEIRA E ÚLTIMA) */}
      {loadedData && !loadedData.error && (
        <section style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
          <h2>
            2. Estrutura de Páginas ({loadedData.totalWords?.toLocaleString() || 0} palavras em {loadedData.totalPages || 0} páginas)
          </h2>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div style={{ flex: 1, background: '#f9f9f9', padding: '10px', borderRadius: '4px' }}>
              <h3>Primeira Página (Página #{loadedData.firstPage?.pageNumber || 1})</h3>
              <ul>
                {loadedData.firstPage?.records?.map((word, i) => <li key={i}>{word}</li>)}
              </ul>
            </div>
            <div style={{ flex: 1, background: '#f9f9f9', padding: '10px', borderRadius: '4px' }}>
              <h3>Última Página (Página #{loadedData.lastPage?.pageNumber || 1})</h3>
              <ul>
                {loadedData.lastPage?.records?.map((word, i) => <li key={i}>{word}</li>)}
              </ul>
            </div>
          </div>
        </section>
      )}

      {/* 3. MÉTRICAS E ESTATÍSTICAS DO HASH */}
      {indexData && (
        <section style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', marginBottom: '20px', background: '#eef6ff', color: '#1a1a1a' }}>
          <h2>3. Estatísticas do Índice Hash</h2>
          <p><strong>Total de Buckets (NB):</strong> {indexData.totalBuckets}</p>
          <p><strong>Tempo de Construção:</strong> {indexData.buildTimeMs} ms</p>
          <p><strong>Taxa de Colisões:</strong> {indexData.collisionRate}%</p>
          <p><strong>Taxa de Overflow:</strong> {indexData.overflowRate}%</p>
        </section>
      )}

      {/* VISUALIZADOR DE BUCKETS REAL (CA28) */}
      {indexData && (
        <section style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
          <h2>5. Visualizador de Buckets (CA28)</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '10px' }}>
            {(indexData.bucketsPage || mockData.bucketsPage).map((bucket) => (
              <div 
                key={bucket.id} 
                style={{ 
                  border: searchResult?.index?.bucketIndex === bucket.id ? '2px solid #70ad47' : '1px solid #ddd',
                  backgroundColor: searchResult?.index?.bucketIndex === bucket.id ? '#e2f0d9' : '#fafafa',
                  padding: '10px', 
                  borderRadius: '6px' 
                }}
              >
                <strong>Bucket #{bucket.id}</strong>
                <ul style={{ paddingLeft: '20px', margin: '5px 0 0 0' }}>
                  {bucket.keys.length > 0 ? (
                    bucket.keys.map((k, i) => (
                      <li key={i} style={{ fontWeight: k.key === searchKey ? 'bold' : 'normal' }}>
                        {k.key} &rarr; Pág #{k.page}
                      </li>
                    ))
                  ) : (
                    <li style={{ color: '#888', listStyle: 'none' }}><em>Vazio</em></li>
                  )}
                </ul>
              </div>
            ))}
          </div>
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
            <button 
              onClick={handleSearchIndex} 
              disabled={loading}
              style={{ padding: '8px 16px', cursor: loading ? 'not-allowed' : 'pointer' }}
            >
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </div>

          {searchResult && (
            <div>
              <h3>Resultado da Comparação:</h3>
              <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#eee' }}>
                    <th>Métrica</th>
                    <th>Busca por Índice</th>
                    <th>Table Scan (Epic 5)</th>
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
                    <td>{searchResult.index.pageNumber > -1 ? `Página #${searchResult.index.pageNumber}` : 'N/A'}</td>
                    <td>{searchResult.scan.pageNumber > -1 ? `Página #${searchResult.scan.pageNumber}` : 'N/A'}</td>
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

              {/* MÉTRICAS COMPARATIVAS DO EPIC 05 */}
              {searchResult.comparison && (
                <div style={{ marginTop: '15px', padding: '12px', background: '#eef6ff', border: '1px solid #b6d4fe', borderRadius: '4px', color: '#1a1a1a' }}>
                  <strong>Métricas Comparativas (Epic 5):</strong>
                  <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px' }}>
                    <li><strong>Redução Percentual de Custo:</strong> {searchResult.comparison.costReductionPct}%</li>
                    <li><strong>Ganho Percentual de Desempenho de Tempo:</strong> {searchResult.comparison.timeDifferencePct}%</li>
                  </ul>
                </div>
              )}

              {/* DESTAQUE VISUAL (CA29) */}
              <div style={{ marginTop: '10px', padding: '10px', background: '#e2f0d9', border: '1px solid #70ad47', borderRadius: '4px', color: '#1a1a1a' }}>
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