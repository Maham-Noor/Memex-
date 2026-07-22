import { FormEvent, useMemo, useState } from "react";

type SearchResult = {
  captureId: string;
  title: string;
  snippet: string;
  url: string;
  score: number;
};

type SearchResponse = {
  status: string;
  results: SearchResult[];
};

const Home = () => {
  const [query, setQuery] = useState("recent ai articles");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const history = useMemo(
    () => results.map((result) => ({ id: result.captureId, title: result.title, url: result.url })),
    [results]
  );

  const handleSearch = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/search/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 5 }),
      });

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const payload: SearchResponse = await response.json();
      setResults(payload.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "Arial, sans-serif", maxWidth: "980px", margin: "0 auto" }}>
      <h1>Memex</h1>
      <p>Search your browser memory with semantic recall.</p>

      <form onSubmit={handleSearch} style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem" }}>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Try: recent ai articles"
          style={{ flex: 1, padding: "0.75rem", borderRadius: "8px", border: "1px solid #ccc" }}
        />
        <button type="submit" style={{ padding: "0.75rem 1rem", borderRadius: "8px", border: "none", background: "#2563eb", color: "white", cursor: "pointer" }}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error ? <p style={{ color: "#b91c1c" }}>{error}</p> : null}

      <section style={{ display: "grid", gap: "1rem", gridTemplateColumns: "2fr 1fr" }}>
        <div>
          <h2>Results</h2>
          {results.length === 0 && !loading ? (
            <p>No results yet. Try a search.</p>
          ) : (
            results.map((result) => (
              <article key={result.captureId} style={{ border: "1px solid #e5e7eb", borderRadius: "10px", padding: "1rem", marginBottom: "0.75rem" }}>
                <h3 style={{ margin: "0 0 0.25rem" }}>{result.title}</h3>
                <p style={{ margin: "0 0 0.25rem" }}>{result.snippet}</p>
                <a href={result.url} target="_blank" rel="noreferrer" style={{ color: "#2563eb" }}>
                  {result.url}
                </a>
                <p style={{ margin: "0.25rem 0 0", color: "#64748b" }}>Relevance: {result.score.toFixed(2)}</p>
              </article>
            ))
          )}
        </div>

        <aside>
          <h2>Recent History</h2>
          {history.length === 0 ? (
            <p>No history yet.</p>
          ) : (
            <ul style={{ paddingLeft: "1rem" }}>
              {history.map((item) => (
                <li key={item.id} style={{ marginBottom: "0.5rem" }}>
                  <strong>{item.title}</strong>
                  <br />
                  <span style={{ color: "#64748b" }}>{item.url}</span>
                </li>
              ))}
            </ul>
          )}
        </aside>
      </section>
    </main>
  );
};

export default Home;
