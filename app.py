import streamlit as st
import anthropic
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="CineMatch – AI Movie Recommender", page_icon="🎬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #0a0a0f; }
.block-container { padding-top: 2rem; max-width: 1000px; }

.hero {
    text-align: center;
    padding: 2rem 0 1.5rem;
}
.hero-eyebrow {
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 700;
    color: #f0e8d8;
    line-height: 1.1;
}
.hero-title em { color: #c9a84c; font-style: italic; }
.hero-sub { font-size: 14px; color: #6a6070; margin-top: 0.5rem; }

.movie-card {
    background: #14141c;
    border: 1px solid #1e1c28;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.movie-card:hover { border-color: rgba(201,168,76,0.4); }

.card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.industry-badge {
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    font-weight: 500;
}
.badge-Hollywood  { background:#1e2a3a; color:#4a8abf; }
.badge-Bollywood  { background:#2a1e1a; color:#c97060; }
.badge-Tollywood  { background:#1e2a1e; color:#5aa05a; }
.badge-Korean     { background:#2a1e2a; color:#a07ab0; }
.badge-other      { background:#2a2820; color:#c0a040; }

.match-score { font-size: 12px; color: #c9a84c; font-weight: 500; }
.movie-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0e8d8;
    margin-bottom: 0.2rem;
}
.movie-meta { font-size: 12px; color: #5a5570; margin-bottom: 0.5rem; }
.genre-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 0.6rem; }
.genre-tag {
    font-size: 10px;
    background: #0a0a0f;
    border: 1px solid #2a2830;
    border-radius: 4px;
    padding: 2px 7px;
    color: #6a6070;
}
.movie-reason {
    font-size: 13px;
    color: #8a8070;
    line-height: 1.55;
    border-top: 1px solid #1e1c28;
    padding-top: 0.6rem;
    margin-top: 0.4rem;
}
.section-label {
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #5a5570;
    margin-bottom: 0.5rem;
}
.stButton > button {
    background: #c9a84c !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stButton > button:hover { background: #e0bc60 !important; }
.stTextInput > div > div > input {
    background: #14141c !important;
    border: 1px solid #2a2830 !important;
    border-radius: 8px !important;
    color: #e8e0d0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox > div > div {
    background: #14141c !important;
    border: 1px solid #2a2830 !important;
    color: #e8e0d0 !important;
}
hr { border-color: #1a1828; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-eyebrow">AI-Powered Discovery</p>
  <h1 class="hero-title">Find Your Next <em>Favourite Film</em></h1>
  <p class="hero-sub">Hollywood · Bollywood · Tollywood · Korean · World Cinema</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Sidebar: API key ──────────────────────────────────────────────────────────


api_key = os.getenv("ANTHROPIC_API_KEY")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    st.markdown("**Filter by Industry**")
    industry_filter = st.selectbox("", ["All", "Hollywood", "Bollywood", "Tollywood", "Korean", "World Cinema"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Quick Searches**")
    quick_picks = ["Interstellar", "3 Idiots", "RRR", "Parasite", "Baahubali", "The Dark Knight", "Dangal", "Dune"]
    for pick in quick_picks:
        if st.button(pick, key=f"quick_{pick}", use_container_width=True):
            st.session_state["movie_query"] = pick
            st.session_state["trigger_search"] = True

# ── Search bar ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    movie_query = st.text_input(
        "", placeholder="e.g. Interstellar, 3 Idiots, RRR, Parasite...",
        value=st.session_state.get("movie_query", ""),
        key="movie_input", label_visibility="collapsed"
    )
with col2:
    search_clicked = st.button("Find Similar →", use_container_width=True)

# ── Trigger logic ─────────────────────────────────────────────────────────────
trigger = search_clicked or st.session_state.pop("trigger_search", False)
query = st.session_state.get("movie_query", movie_query) or movie_query

def get_badge_class(industry):
    known = ["Hollywood", "Bollywood", "Tollywood", "Korean"]
    return f"badge-{industry}" if industry in known else "badge-other"

def render_movie_card(m):
    badge_class = get_badge_class(m.get("industry", ""))
    genres_html = "".join(f'<span class="genre-tag">{g}</span>' for g in m.get("genres", []))

    st.markdown(f"""
    <div class="movie-card">
      <div class="card-top">
        <span class="industry-badge {badge_class}">{m.get('industry','')}</span>
        <span class="match-score">{m.get('match_score','')}% match</span>
      </div>

      <p class="movie-title">{m.get('title','')}</p>

      <p class="movie-meta">
        {m.get('year','')} · {m.get('runtime','')} · ⭐ {m.get('imdb_rating','')}
      </p>

      <div class="genre-tags">{genres_html}</div>

      <p class="movie-meta"><b>Country:</b> {m.get('country','')}</p>
      <p class="movie-meta"><b>Director:</b> {m.get('director','')}</p>
      <p class="movie-meta"><b>Cast:</b> {m.get('cast','')}</p>

      <p class="movie-reason">{m.get('plot','')}</p>
    </div>
    """, unsafe_allow_html=True)

def get_movie_details(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "True":
        return {
            "imdb_rating": data.get("imdbRating"),
            "runtime": data.get("Runtime"),
            "year": data.get("Year"),
            "country": data.get("Country"),
            "genres": data.get("Genre", "").split(", "),
            "director": data.get("Director"),
            "cast": data.get("Actors"),
            "plot": data.get("Plot")
        }
    return {}
    
# ── Search & render ───────────────────────────────────────────────────────────
if trigger and query:
    if not api_key or not OMDB_API_KEY:
       st.error("API keys not configured. Please check your .env file.")
       st.stop()
    else:
        filter_note = (
            "Include movies from Hollywood, Bollywood, Tollywood, Korean cinema, Japanese, European and other world cinemas."
            if industry_filter == "All"
            else f"Focus primarily on {industry_filter} films but include a couple from other industries if very similar."
        )
        prompt = f"""You are a world-class film expert. The user wants movies similar to: "{query}"

Return EXACTLY 8 movie recommendations as a valid JSON array. No markdown, no explanation, pure JSON only.

Each object must have:
- "title": string
- "year": number
- "industry": one of Hollywood/Bollywood/Tollywood/Korean/Japanese/European/World Cinema
- "director": string
- "genres": array of 2-4 strings
- "match_score": number 70-99
- "reason": 1-2 sentences explaining why it is similar

{filter_note}

Return ONLY the JSON array."""

        with st.spinner(f"Analysing *{query}* and finding matches..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = message.content[0].text.strip()
                clean = raw.replace("```json", "").replace("```", "").strip()
                movies = json.loads(clean)
                for m in movies:
                    details = get_movie_details(m["title"])
    
                    if details:
                        m.update(details)
                movies.sort(key=lambda x: x.get("match_score", 0), reverse=True)

                if industry_filter != "All":
                    filtered = [m for m in movies if industry_filter.lower() in m.get("industry", "").lower()]
                    movies = filtered if filtered else movies

                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:1rem;">
                  <p style="font-family:'Playfair Display',serif; font-size:1.1rem; font-style:italic; color:#b0a898;">
                    Because you liked <em>{query}</em>...
                  </p>
                  <span style="font-size:12px; color:#5a5570;">{len(movies)} films found</span>
                </div>
                """, unsafe_allow_html=True)

                cols = st.columns(2)
                for i, m in enumerate(movies):
                    with cols[i % 2]:
                        render_movie_card(m)

            except json.JSONDecodeError:
                st.error("Could not parse recommendations. Please try again.")
            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your key in the sidebar.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

elif not trigger:
    st.markdown('<p class="section-label" style="text-align:center; padding:2rem 0 0.5rem;">Type a movie name above or pick one from the sidebar to get started</p>', unsafe_allow_html=True)
