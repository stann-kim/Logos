import { useState } from "react"

export default function App() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  async function handleSearch() {
    if (!query.trim()) return
    setLoading(true)
    const res = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`)
    const data = await res.json()
    setResults(data.results)
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 700, margin: "60px auto", fontFamily: "Georgia, serif", padding: "0 20px" }}>
      <h1 style={{ fontSize: 32, marginBottom: 4 }}>Logos</h1>
      <p style={{ color: "#666", marginBottom: 24 }}>Search the Bible by meaning, not just keywords</p>

      <div style={{ display: "flex", gap: 8, marginBottom: 32 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSearch()}
          placeholder="e.g. feeling anxious and overwhelmed..."
          style={{ flex: 1, padding: "10px 14px", fontSize: 16, border: "1px solid #ccc", borderRadius: 6 }}
        />
        <button
          onClick={handleSearch}
          style={{ padding: "10px 20px", fontSize: 16, background: "#1a1a1a", color: "white", border: "none", borderRadius: 6, cursor: "pointer" }}
        >
          Search
        </button>
      </div>

      {loading && <p style={{ color: "#666" }}>Searching...</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {results.map((r, i) => (
          <div key={i} style={{ padding: 16, border: "1px solid #eee", borderRadius: 8 }}>
            <p style={{ margin: "0 0 8px 0", fontSize: 15, lineHeight: 1.6 }}>{r.text}</p>
            <p style={{ margin: 0, fontSize: 13, color: "#888" }}>
              {r.book} {r.chapter}:{r.verse} · {Math.round(r.similarity * 100)}% match
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}