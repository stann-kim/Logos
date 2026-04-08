import { useState } from "react"
import "./index.css"

export default function App() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  async function handleSearch() {
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    try {
      const res = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`)
      const data = await res.json()
      setResults(data.results)
    } catch (e) {
      setResults([])
    }
    setLoading(false)
  }

  return (
    <div style={{
      minHeight: "100vh",
      width: "100%",
      background: "linear-gradient(135deg, #0d4f6e, #0a7c8c, #00b4cc, #0077b6, #006994, #0a9396)",
      backgroundSize: "400% 400%",
      animation: "underwaterShift 14s linear infinite",
      fontFamily: "'Georgia', serif",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* Ambient orbs */}
      <div style={{
        position: "fixed", top: "-20vh", right: "-10vw",
        width: "55vw", height: "55vw",
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(0,180,220,0.2) 0%, transparent 70%)",
        pointerEvents: "none", zIndex: 0,
      }} />
      <div style={{
        position: "fixed", bottom: "-15vh", left: "-10vw",
        width: "50vw", height: "50vw",
        borderRadius: "50%",
        background: "radial-gradient(circle, rgba(0,100,160,0.25) 0%, transparent 70%)",
        pointerEvents: "none", zIndex: 0,
      }} />

      {/* Hero */}
      <div style={{
        width: "660px",
        maxWidth: "calc(100% - 40px)",
        margin: "0 auto",
        padding: "14vh 0 3rem 0",
        position: "relative",
        zIndex: 1,
      }}>
        <p style={{
          fontSize: 11, fontWeight: 600, letterSpacing: "0.2em",
          textTransform: "uppercase", color: "rgba(255,255,255,0.95)",
          marginBottom: "1.5rem",
          textShadow: "0 0 20px rgba(255,255,255,0.2)",
        }}>
          Logos
        </p>
        <h1 style={{
          fontSize: 48, fontWeight: 400, lineHeight: 1.15,
          color: "rgba(255,255,255,0.95)", margin: "0 0 1rem 0",
          textShadow: "0 0 40px rgba(255,255,255,0.3)",
        }}>
          Search scripture<br />by meaning.
        </h1>
        <p style={{
          fontSize: 15, color: "rgba(255,255,255,0.75)",
          lineHeight: 1.7, margin: "0 0 2.5rem 0",
          fontFamily: "sans-serif",
        }}>
          Find verses that speak to what you're going through —<br />
          not just what you remember word for word.
        </p>

        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSearch()}
            placeholder="e.g. feeling anxious and overwhelmed..."
            style={{
              flex: 1, height: 48, padding: "0 16px", fontSize: 15,
              fontFamily: "sans-serif",
              background: "rgba(255,255,255,0.12)",
              border: "0.5px solid rgba(255,255,255,0.25)",
              borderRadius: 12, color: "rgba(255,255,255,0.95)",
              outline: "none",
              backdropFilter: "blur(16px)",
              WebkitBackdropFilter: "blur(16px)",
            }}
          />
          <button
            onClick={handleSearch}
            style={{
              height: 48, padding: "0 22px", fontSize: 14,
              fontFamily: "sans-serif", fontWeight: 500,
              background: "rgba(255,255,255,0.18)",
              border: "0.5px solid rgba(255,255,255,0.3)",
              borderRadius: 12, color: "rgba(255,255,255,0.95)",
              cursor: "pointer",
              backdropFilter: "blur(16px)",
              WebkitBackdropFilter: "blur(16px)",
              transition: "background 0.2s",
            }}
            onMouseEnter={e => e.target.style.background = "rgba(255,255,255,0.25)"}
            onMouseLeave={e => e.target.style.background = "rgba(255,255,255,0.18)"}
          >
            Search
          </button>
        </div>
      </div>

      {/* Results */}
      <div style={{
        width: "660px",
        maxWidth: "calc(100% - 40px)",
        margin: "0 auto",
        padding: "0 0 5rem 0",
        position: "relative",
        zIndex: 1,
      }}>
        {loading && (
          <p style={{ color: "rgba(255,255,255,0.6)", fontSize: 13, fontFamily: "sans-serif" }}>
            Searching...
          </p>
        )}
        {!loading && results.map((r, i) => (
          <div key={i}
            style={{
              background: "rgba(255,255,255,0.08)",
              border: "0.5px solid rgba(255,255,255,0.15)",
              borderRadius: 16, padding: "1.25rem 1.5rem",
              marginBottom: 10,
              backdropFilter: "blur(20px)",
              WebkitBackdropFilter: "blur(20px)",
              transition: "background 0.2s",
            }}
            onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.13)"}
            onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.08)"}
          >
            <p style={{
              fontSize: 15, lineHeight: 1.75,
              color: "rgba(255,255,255,0.95)",
              margin: "0 0 14px 0",
              textShadow: "0 0 20px rgba(255,255,255,0.1)",
              textAlign: "left",
            }}>
              {r.text}
            </p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{
                fontSize: 12, fontWeight: 500,
                letterSpacing: "0.06em",
                color: "rgba(255,255,255,0.95)",
                textShadow: "0 0 20px rgba(255,255,255,0.1)",
                textAlign: "left"
              }}>
                {r.book} {r.chapter}:{r.verse}
              </span>
              <span style={{
                fontSize: 11,
                color: "rgba(255,255,255,0.4)",
                fontFamily: "sans-serif",
              }}>
                {Math.round(r.similarity * 100)}% match
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}