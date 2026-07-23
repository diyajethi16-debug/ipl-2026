# 🏏 IPL 2026 Analytics Dashboard

A Streamlit data-science project built on ball-by-ball IPL 2026 delivery data (74 matches, 17,477 deliveries).

## Features

### 🔧 Global interactive filters (sidebar, apply across every page)
Tournament stage, teams, venue, and date range — the whole dashboard (including the ML model) recomputes live against your filtered slice of the season.

### Pages
- **Overview** — season KPIs, team win counts, top scorers/wicket-takers (adjustable Top-N sliders), runs-per-over trend, batting-phase pie, and a bat-first vs chase win-rate breakdown
- **Team Analysis** — win %, chase win %, phase-wise runs & run rate, top batters/bowlers per team, and a team-vs-team scatter comparison (toggle between two metric views)
- **Player Stats** — three tabs: sortable Batting leaderboard (with dot%/boundary%), sortable Bowling leaderboard, and a **Phase Specialists** finder (best powerplay/death strike rates or economies)
- **Player Comparison** *(new)* — pick any two batters or bowlers and see a radar-chart comparison plus phase-wise strike rate / economy bars
- **Venue Analysis** *(new)* — average 1st-innings score and chase-win% per venue, with a drill-down into any venue's match list
- **Match Explorer** — pick any match: score, winner, worm chart (now with wickets marked), a Manhattan (runs-per-over) chart, wicket timeline, and ball-by-ball CSV export
- **Head-to-Head** — compare any two teams' season record, with a score-trend line chart across their meetings
- **Win Predictor** — logistic regression trained on 2nd-innings match states (runs needed, balls left, wickets in hand); shows a live win-probability gauge plus a "how probability would evolve" curve as balls run out — retrains automatically on your current filters

### Functionality
- CSV export buttons on every major table (team stats, player stats, venue stats, match/H2H data)
- All charts are interactive Plotly (zoom, hover tooltips, legend toggling)
- Sliders/selectors for minimum balls/overs thresholds so leaderboards aren't skewed by small samples

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Project structure

```
ipl_project/
├── app.py                       # main Streamlit app
├── requirements.txt
├── data/
│   └── ipl_2026_deliveries.csv  # ball-by-ball dataset
└── README.md
```

## Data notes

- Match winners are derived (not given directly) by summing each team's runs across all its innings in a match — this also gracefully handles the super-over matches in the data.
- "Batting phase" (Powerplay/Middle/Death) is derived from the `over` column, not the `phase` column (which refers to tournament stage: Group Stage, Qualifiers, Final).
- The Win Predictor is trained fresh each time the app starts (cached with `st.cache_resource`), sampling every 3rd ball of 2nd innings across all matches to keep training fast — it's meant as a demonstrative ML feature, not a production-grade model.
