import { useState } from "react";
import "./App.css";

const QUICK = ["Interstellar", "3 Idiots", "RRR", "Parasite", "Baahubali", "The Dark Knight", "Dangal", "Dune"];
const FILTERS = ["All", "Hollywood", "Bollywood", "Tollywood", "Korean", "World Cinema"];

const BADGE_COLOR = { Hollywood: "#4a8abf", Bollywood: "#c97060", Tollywood: "#5aa05a", Korean: "#a07ab0" };
const BADGE_BG = { Hollywood: "#1e2a3a", Bollywood: "#2a1e1a", Tollywood: "#1e2a1e", Korean: "#2a1e2a" };

function getBadge(industry) {
  return { color: BADGE_COLOR[industry] || "#c0a040", background: BADGE_BG[industry] || "#2a2820" };
}

export default function App() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(false);
  const [movies, setMovies] = useState([]);
  const [searched, setSearched] = useState("");
  const [error, setError] = useState("");

  async function findSimilar(q = query) {
    if (!q.trim()) return;
    setLoading(true);
    setError("");
    setMovies([]);
    setSearched(q);

    const filterNote =
      filter === "All"
        ? "Include movies from Hollywood, Bollywood, Tollywood, Korean cinema, Japanese, European and other world cinemas."
        : `Focus primarily on ${filter} films but include a couple from other industries if very similar.`;

    const prompt = `You are a world-class film expert. The user wants movies similar to: "${q}"

Return EXACTLY 8 movie recommendations as a valid JSON array. No markdown, no explanation, pure JSON only.

Each object must have:
- "title": string
- "year": number
- "industry": one of Hollywood/Bollywood/Tollywood/Korean/Japanese/European/World Cinema
- "director": string
- "genres": array of 2-4 strings
- "match_score": number 70-99
- "reason": 1-2 sentences explaining why it is similar

${filterNote}

Return ONLY the JSON array.`;

    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": import.meta.env.VITE_ANTHROPIC_API_KEY,
          "anthropic-version": "2023-06-01",
          "anthropic-dangerous-direct-browser-access": "true",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1500,
          messages: [{ role: "user", content: prompt }],
        }),
      });

      const data = await res.json();
      if (data.error) {
        setError("API error: " + data.error.message);
        setLoading(false);
        return;
      }

      const text = data.content.map((b) => b.text || "").join("");
      const clean = text.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      setMovies(parsed.sort((a, b) => b.match_score - a.match_score));
    } catch (e) {
      setError("Something went wrong. Check your API key and try again.");
      console.error(e);
    }

    setLoading(false);
  }

  const displayed =
    filter === "All"
      ? movies
      : movies.filter((m) => m.industry.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="app">
      {/* Hero */}
      <div className="hero">
        <p className="eyebrow">AI-Powered Discovery</p>
        <h1 className="hero-title">
          Find Your Next <em>Favourite Film</em>
        </h1>
        <p className="hero-sub">Hollywood · Bollywood · Tollywood · Korean · World Cinema</p>
      </div>

      {/* Search */}
      <div className="search-area">
        <div className="search-row">
          <input
            className="search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && findSimilar()}
            placeholder="e.g. Interstellar, 3 Idiots, RRR, Parasite..."
          />
          <button className="search-btn" onClick={() => findSimilar()} disabled={loading}>
            {loading ? "Searching..." : "Find Similar →"}
          </button>
        </div>

        {/* Filters */}
        <div className="filters">
          <span className="filter-label">Filter:</span>
          {FILTERS.map((f) => (
            <button
              key={f}
              className={`filter-chip ${filter === f ? "active" : ""}`}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Quick Picks */}
      {movies.length === 0 && !loading && (
        <div className="quick-picks">
          <p className="section-label">Popular searches</p>
          <div className="quick-grid">
            {QUICK.map((t) => (
              <button key={t} className="quick-pill" onClick={() => { setQuery(t); findSimilar(t); }}>
                {t}
              </button>
            ))}
          </div>
        </div>
      )}

      <hr className="divider" />

      {/* Loading */}
      {loading && (
        <div className="status-bar">
          <span className="spinner" />
          Analysing <em>{searched}</em> and finding matches...
        </div>
      )}

      {/* Error */}
      {error && <div className="error-msg">{error}</div>}

      {/* Results */}
      {displayed.length > 0 && (
        <>
          <div className="results-header">
            <p className="results-title">
              Because you liked <em>{searched}</em>...
            </p>
            <span className="results-count">{displayed.length} films</span>
          </div>

          <div className="movies-grid">
            {displayed.map((m, i) => {
              const b = getBadge(m.industry);
              return (
                <div key={i} className="movie-card">
                  <div className="card-top">
                    <span className="industry-badge" style={{ background: b.background, color: b.color }}>
                      {m.industry}
                    </span>
                    <span className="match-score">{m.match_score}% match</span>
                  </div>
                  <p className="movie-title">{m.title}</p>
                  <p className="movie-meta">{m.year} · {m.director}</p>
                  <div className="genre-tags">
                    {(m.genres || []).map((g, j) => (
                      <span key={j} className="genre-tag">{g}</span>
                    ))}
                  </div>
                  <p className="movie-reason">{m.reason}</p>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
