export const mockData = {
  // Resposta do /load-data
  loadData: {
    totalWords: 466551,
    totalPages: 467,
    pageSize: 1000,
    firstPage: {
      pageNumber: 1,
      records: ["a", "aa", "aal", "aalii", "aam"]
    },
    lastPage: {
      pageNumber: 467,
      records: ["zyzzogeton", "zymocyte", "zymogene", "zymogenic", "zymology"]
    }
  },

  // Resposta do /build-index
  buildIndex: {
    totalBuckets: 50000,
    bucketCapacity: 10,
    buildTimeMs: 124.5,
    collisionRate: 12.3, // %
    overflowRate: 2.1    // %
  },

  // Resposta do /buckets?page=1&limit=5
  bucketsPage: [
    { id: 0, keys: [{ key: "a", page: 1 }, { key: "aa", page: 1 }] },
    { id: 1, keys: [{ key: "aal", page: 1 }] },
    { id: 2, keys: [{ key: "aalii", page: 1 }, { key: "aam", page: 1 }] },
    { id: 3, keys: [] },
    { id: 4, keys: [{ key: "zyzzogeton", page: 467 }] }
  ],

  // Resposta do /search
  searchIndexResult: {
    found: true,
    key: "aam",
    pageNumber: 1,
    bucketIndex: 2,
    costPagesRead: 1,
    timeMs: 0.12
  },

  searchScanResult: {
    found: true,
    key: "aam",
    pageNumber: 1,
    costPagesRead: 1,
    timeMs: 4.8
  }
};