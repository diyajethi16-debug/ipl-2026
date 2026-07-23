
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="IPL 2026 Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEAM_COLORS = {
    "CSK": "#FDB913", "MI": "#004BA0", "RCB": "#EC1C24", "KKR": "#3A225D",
    "SRH": "#F26522", "DC": "#17449B", "RR": "#EA1A85", "PBKS": "#DD1F2D",
    "GT": "#1B2133", "LSG": "#00AEEF",
}

# ----------------------------------------------------------------------------
# THEME — "Night Match" scoreboard palette
# ----------------------------------------------------------------------------
BG = "#0A0E1A"
PANEL = "#131B2C"
BORDER = "#223049"
TEXT = "#ECEFF4"
MUTED = "#8996AD"
GOLD = "#F2B705"    # floodlight
RED = "#E63946"     # ball seam
GREEN = "#2ECC71"   # turf

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

:root {{
  --bg: {BG}; --panel: {PANEL}; --border: {BORDER};
  --text: {TEXT}; --muted: {MUTED}; --gold: {GOLD}; --red: {RED}; --green: {GREEN};
}}

html, body, [data-testid="stAppViewContainer"], .main {{
  background-color: var(--bg) !important;
  color: var(--text);
  font-family: 'Inter', sans-serif;
}}
[data-testid="stAppViewContainer"] > .main {{
  background-image: radial-gradient(ellipse 900px 400px at top, rgba(242,183,5,0.07), transparent 65%);
}}

h1, h2, h3 {{ font-family: 'Oswald', sans-serif !important; letter-spacing: 0.4px; color: var(--text) !important; }}

/* Page hero header */
.ipl-header {{ display: flex; align-items: baseline; gap: 12px; margin: 0 0 2px 0; }}
.ipl-header .ipl-emoji {{ font-size: 1.9rem; }}
.ipl-header .ipl-title {{
  font-family: 'Oswald', sans-serif; font-size: 2.1rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 1px; color: var(--text);
  border-bottom: 3px solid var(--gold); padding-bottom: 6px;
}}
.ipl-subtitle {{ color: var(--muted); font-size: 0.92rem; margin: 6px 0 18px 0; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background-color: var(--panel) !important; border-right: 1px solid var(--border); }}
[data-testid="stSidebar"] h1 {{ color: var(--gold) !important; font-size: 1.5rem; border: none; }}
[data-testid="stSidebar"] h3 {{ color: var(--muted) !important; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }}

/* Metric cards — scoreboard tiles */
[data-testid="stMetric"] {{
  background: var(--panel); border: 1px solid var(--border); border-left: 4px solid var(--gold);
  border-radius: 10px; padding: 12px 16px 10px 16px;
}}
[data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono', monospace !important; color: var(--gold) !important; font-weight: 700; }}
[data-testid="stMetricLabel"] {{ text-transform: uppercase; letter-spacing: 1px; color: var(--muted) !important; font-size: 0.72rem !important; }}
[data-testid="stMetricDelta"] {{ font-family: 'Inter', sans-serif !important; }}

/* Buttons */
.stButton>button, .stDownloadButton>button {{
  background-color: transparent; color: var(--gold); border: 1px solid var(--gold);
  border-radius: 6px; font-weight: 600; transition: 0.15s ease;
}}
.stButton>button:hover, .stDownloadButton>button:hover {{ background-color: var(--gold); color: #0A0E1A; }}

/* Dataframes / tables */
[data-testid="stDataFrame"] {{ border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }}

/* Tabs */
button[data-baseweb="tab"] {{ font-family: 'Oswald', sans-serif; letter-spacing: 0.5px; color: var(--muted); }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: var(--gold) !important; }}
[data-baseweb="tab-highlight"] {{ background-color: var(--gold) !important; }}
[data-baseweb="tab-border"] {{ background-color: var(--border) !important; }}

/* Multiselect chips */
span[data-baseweb="tag"] {{ background-color: var(--red) !important; border-radius: 4px !important; }}

/* Expander */
[data-testid="stExpander"] {{ border: 1px solid var(--border); border-radius: 8px; background: var(--panel); }}

/* Sliders */
[data-testid="stSlider"] div[role="slider"] {{ background-color: var(--gold) !important; }}
.stSlider [data-baseweb="slider"] > div > div {{ background: var(--gold) !important; }}

hr {{ border-color: var(--border) !important; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# PLOTLY THEME — match the scoreboard palette, transparent so it blends in
# ----------------------------------------------------------------------------
_tpl = go.layout.Template(pio.templates["plotly_dark"])
_tpl.layout.paper_bgcolor = "rgba(0,0,0,0)"
_tpl.layout.plot_bgcolor = "rgba(0,0,0,0)"
_tpl.layout.font = dict(family="Inter, sans-serif", color=TEXT, size=13)
_tpl.layout.title.font = dict(family="Oswald, sans-serif", size=19, color=TEXT)
_tpl.layout.colorway = [GOLD, RED, GREEN, "#4EA8DE", "#9B5DE5", "#F15BB5", "#00BBF9", "#FEE440", "#F26522", "#3A225D"]
_tpl.layout.xaxis.gridcolor = BORDER
_tpl.layout.yaxis.gridcolor = BORDER
_tpl.layout.xaxis.linecolor = BORDER
_tpl.layout.yaxis.linecolor = BORDER
_tpl.layout.legend.font = dict(color=TEXT)
pio.templates["ipl2026"] = _tpl
pio.templates.default = "ipl2026"


def page_header(emoji, title, subtitle=None):
    """Styled scoreboard-style page hero, replaces st.title()."""
    st.markdown(
        f'<div class="ipl-header"><span class="ipl-emoji">{emoji}</span>'
        f'<span class="ipl-title">{title}</span></div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f'<div class="ipl-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def csv_download_button(dataframe, label, filename):
    st.download_button(
        label=f"⬇️ {label}",
        data=dataframe.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )

# ----------------------------------------------------------------------------
# DATA LOADING & FEATURE ENGINEERING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/ipl_2026_deliveries.csv")
    df["date"] = pd.to_datetime(df["date"], format="%b %d, %Y")
    df["total_runs"] = df["runs_of_bat"] + df["extras"]
    df["is_wicket"] = df["wicket_type"].notna().astype(int)
    df["is_legal_ball"] = ((df["wide"] == 0) & (df["noballs"] == 0)).astype(int)
    df["ball_phase"] = pd.cut(
        df["over"], bins=[-0.1, 5.999, 14.999, 20],
        labels=["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"]
    )
    df["is_boundary4"] = (df["runs_of_bat"] == 4).astype(int)
    df["is_boundary6"] = (df["runs_of_bat"] == 6).astype(int)
    df["is_dot_batter"] = ((df["wide"] == 0) & (df["runs_of_bat"] == 0)).astype(int)
    df["is_dot_bowler"] = ((df["is_legal_ball"] == 1) & (df["runs_of_bat"] + df["byes"] + df["legbyes"] == 0)).astype(int)
    return df


@st.cache_data
def build_match_summary(df):
    rows = []
    for match_id, g in df.groupby("match_id"):
        info = g.iloc[0]
        innings_totals = g.groupby(["innings", "batting_team"])["total_runs"].sum()
        innings_wkts = g.groupby(["innings", "batting_team"])["is_wicket"].sum()
        innings_list = sorted(g["innings"].unique())
        team_scores = {}
        for inn in innings_list:
            sub = innings_totals.xs(inn, level="innings")
            for team, score in sub.items():
                team_scores.setdefault(team, 0)
                team_scores[team] += score
        wkts = {}
        for inn in innings_list:
            sub = innings_wkts.xs(inn, level="innings")
            for team, w in sub.items():
                wkts.setdefault(team, 0)
                wkts[team] += w

        teams = list(team_scores.keys())
        if len(teams) < 2:
            continue
        t1, t2 = teams[0], teams[1]
        s1, s2 = team_scores[t1], team_scores[t2]
        if s1 == s2:
            winner, margin = "Tie/No Result", 0
        elif s1 > s2:
            winner, margin = t1, s1 - s2
        else:
            winner, margin = t2, s2 - s1

        # who batted first vs chased (innings 1 batting team)
        first_batting_team = g[g["innings"] == innings_list[0]]["batting_team"].iloc[0]
        chasing_team = t2 if first_batting_team == t1 else t1

        rows.append({
            "match_id": match_id,
            "date": info["date"],
            "phase": info["phase"],
            "match_no": info["match_no"],
            "venue": info["venue"],
            "team1": t1,
            "team2": t2,
            "score1": s1,
            "score2": s2,
            "wkts1": wkts.get(t1, 0),
            "wkts2": wkts.get(t2, 0),
            "winner": winner,
            "margin": margin,
            "first_batting_team": first_batting_team,
            "chasing_team": chasing_team,
            "chase_successful": winner == chasing_team,
        })
    return pd.DataFrame(rows)


@st.cache_data
def build_batting_stats(df):
    balls_faced = df[df["wide"] == 0].groupby("striker").size().rename("balls_faced")
    runs = df.groupby("striker")["runs_of_bat"].sum().rename("runs")
    fours = df.groupby("striker")["is_boundary4"].sum().rename("fours")
    sixes = df.groupby("striker")["is_boundary6"].sum().rename("sixes")
    dots = df[df["wide"] == 0].groupby("striker")["is_dot_batter"].sum().rename("dots")
    matches = df.groupby("striker")["match_id"].nunique().rename("matches")
    dismissals = df.dropna(subset=["player_dismissed"]).groupby("player_dismissed").size().rename("dismissals")

    stats = pd.concat([runs, balls_faced, fours, sixes, dots, matches], axis=1).fillna(0)
    stats = stats.join(dismissals, how="left").fillna({"dismissals": 0})
    stats["strike_rate"] = np.where(stats["balls_faced"] > 0, stats["runs"] / stats["balls_faced"] * 100, 0).round(2)
    stats["average"] = np.where(stats["dismissals"] > 0, stats["runs"] / stats["dismissals"], stats["runs"]).round(2)
    stats["boundary_pct"] = np.where(stats["balls_faced"] > 0, (stats["fours"] + stats["sixes"]) / stats["balls_faced"] * 100, 0).round(1)
    stats["dot_pct"] = np.where(stats["balls_faced"] > 0, stats["dots"] / stats["balls_faced"] * 100, 0).round(1)
    stats = stats.reset_index().rename(columns={"striker": "player"})
    stats = stats.sort_values("runs", ascending=False)
    return stats


@st.cache_data
def build_bowling_stats(df):
    legal_balls = df.groupby("bowler")["is_legal_ball"].sum().rename("balls_bowled")
    runs_conceded = df.groupby("bowler").apply(
        lambda g: (g["runs_of_bat"] + g["wide"] + g["noballs"]).sum()
    ).rename("runs_conceded")
    dots = df.groupby("bowler")["is_dot_bowler"].sum().rename("dots")
    wickets = df[df["wicket_type"].notna() & ~df["wicket_type"].isin(["runout", "obstructing the field", "retired hurt"])]
    wickets = wickets.groupby("bowler").size().rename("wickets")
    matches = df.groupby("bowler")["match_id"].nunique().rename("matches")

    stats = pd.concat([legal_balls, runs_conceded, dots, matches], axis=1).fillna(0)
    stats = stats.join(wickets, how="left").fillna({"wickets": 0})
    stats["overs"] = (stats["balls_bowled"] // 6 + (stats["balls_bowled"] % 6) / 10).round(1)
    stats["economy"] = np.where(stats["balls_bowled"] > 0, stats["runs_conceded"] / (stats["balls_bowled"] / 6), 0).round(2)
    stats["average"] = np.where(stats["wickets"] > 0, stats["runs_conceded"] / stats["wickets"], np.nan).round(2)
    stats["dot_pct"] = np.where(stats["balls_bowled"] > 0, stats["dots"] / stats["balls_bowled"] * 100, 0).round(1)
    stats = stats.reset_index().rename(columns={"bowler": "player"})
    stats = stats.sort_values("wickets", ascending=False)
    return stats


@st.cache_data
def build_team_stats(match_summary):
    teams = sorted(set(match_summary["team1"]).union(match_summary["team2"]))
    rows = []
    for team in teams:
        played = match_summary[(match_summary["team1"] == team) | (match_summary["team2"] == team)]
        wins = (played["winner"] == team).sum()
        losses = len(played) - wins - (played["winner"] == "Tie/No Result").sum()
        total_matches = len(played)
        win_pct = round(wins / total_matches * 100, 1) if total_matches else 0
        avg_score = played.apply(
            lambda r: r["score1"] if r["team1"] == team else r["score2"], axis=1
        ).mean()
        chases = played[played["chasing_team"] == team]
        chase_wins = chases["chase_successful"].sum()
        chase_pct = round(chase_wins / len(chases) * 100, 1) if len(chases) else 0
        rows.append({
            "team": team, "matches": total_matches, "wins": wins,
            "losses": losses, "win_pct": win_pct,
            "avg_score": round(avg_score, 1) if pd.notna(avg_score) else 0,
            "chases_won": chase_wins, "chases_played": len(chases), "chase_win_pct": chase_pct,
        })
    return pd.DataFrame(rows).sort_values("wins", ascending=False)


@st.cache_data
def build_phase_batting(df):
    g = df[df["wide"] == 0].groupby(["striker", "ball_phase"], observed=True).agg(
        runs=("runs_of_bat", "sum"), balls=("runs_of_bat", "size")
    ).reset_index()
    g["strike_rate"] = np.where(g["balls"] > 0, g["runs"] / g["balls"] * 100, 0).round(1)
    return g.rename(columns={"striker": "player"})


@st.cache_data
def build_phase_bowling(df):
    g = df.groupby(["bowler", "ball_phase"], observed=True).agg(
        runs=("runs_of_bat", lambda x: (x + df.loc[x.index, "wide"] + df.loc[x.index, "noballs"]).sum()),
        balls=("is_legal_ball", "sum"),
        wickets=("is_wicket", "sum"),
    ).reset_index()
    g["economy"] = np.where(g["balls"] > 0, g["runs"] / (g["balls"] / 6), 0).round(2)
    return g.rename(columns={"bowler": "player"})


@st.cache_data
def build_venue_stats(match_summary):
    rows = []
    for venue, g in match_summary.groupby("venue"):
        first_scores = g.apply(lambda r: r["score1"] if r["team1"] == r["first_batting_team"] else r["score2"], axis=1)
        chase_win_rate = g["chase_successful"].mean() * 100 if len(g) else 0
        rows.append({
            "venue": venue,
            "matches": len(g),
            "avg_1st_innings_score": round(first_scores.mean(), 1),
            "highest_score": int(max(g["score1"].max(), g["score2"].max())),
            "chase_win_pct": round(chase_win_rate, 1),
        })
    return pd.DataFrame(rows).sort_values("matches", ascending=False)


# ----------------------------------------------------------------------------
# LOAD RAW DATA
# ----------------------------------------------------------------------------

raw_df = load_data()
raw_match_summary = build_match_summary(raw_df)

# ----------------------------------------------------------------------------
# SIDEBAR — GLOBAL INTERACTIVE FILTERS
# ----------------------------------------------------------------------------
st.sidebar.title("🏏 IPL 2026 Dashboard")
st.sidebar.markdown("### 🔧 Filters")

all_stages = sorted(raw_df["phase"].unique())
sel_stages = st.sidebar.multiselect("Tournament stage", all_stages, default=all_stages)

all_teams = sorted(set(raw_df["batting_team"]).union(raw_df["bowling_team"]))
sel_teams = st.sidebar.multiselect("Teams (any match involving)", all_teams, default=all_teams)

all_venues = sorted(raw_df["venue"].unique())
sel_venues = st.sidebar.multiselect("Venue", all_venues, default=all_venues)

min_date, max_date = raw_df["date"].min().date(), raw_df["date"].max().date()
date_range = st.sidebar.slider("Date range", min_value=min_date, max_value=max_date,
                                value=(min_date, max_date))

df = raw_df[
    raw_df["phase"].isin(sel_stages)
    & raw_df["venue"].isin(sel_venues)
    & (raw_df["batting_team"].isin(sel_teams) | raw_df["bowling_team"].isin(sel_teams))
    & (raw_df["date"].dt.date >= date_range[0])
    & (raw_df["date"].dt.date <= date_range[1])
].copy()

if df.empty:
    st.sidebar.error("No data matches these filters — showing full dataset instead.")
    df = raw_df.copy()

if st.sidebar.button("↺ Reset filters"):
    st.rerun()

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Team Analysis", "Player Stats", "Player Comparison",
     "Venue Analysis", "Match Explorer", "Head-to-Head", "Insights"],
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Filtered: {df['match_id'].nunique()} matches · {len(df):,} deliveries "
                    f"(of {raw_df['match_id'].nunique()} matches / {len(raw_df):,} total)")

# ----------------------------------------------------------------------------
# DERIVED TABLES (recomputed on filtered data)
# ----------------------------------------------------------------------------
match_summary = build_match_summary(df)
batting_stats = build_batting_stats(df)
bowling_stats = build_bowling_stats(df)
team_stats = build_team_stats(match_summary)
phase_batting = build_phase_batting(df)
phase_bowling = build_phase_bowling(df)
venue_stats = build_venue_stats(match_summary)

# ----------------------------------------------------------------------------
# PAGE: OVERVIEW
# ----------------------------------------------------------------------------
if page == "Overview":
    page_header("🏏", "IPL 2026 Season Overview", "Headline numbers for the current filter selection")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Matches", df["match_id"].nunique())
    c2.metric("Deliveries", f"{len(df):,}")
    c3.metric("Total Runs", f"{df['total_runs'].sum():,}")
    c4.metric("Sixes", int(df["is_boundary6"].sum()))
    c5.metric("Fours", int(df["is_boundary4"].sum()))

    st.markdown("### Team Standings")
    fig = px.bar(
        team_stats, x="team", y="wins", color="team",
        color_discrete_map=TEAM_COLORS, text="wins",
        title="Wins by Team", hover_data=["matches", "win_pct", "chase_win_pct"],
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    csv_download_button(team_stats, "Download team standings CSV", "team_standings.csv")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top 10 Run Scorers")
        n_bat = st.slider("How many batters to show", 5, 25, 10, key="ov_bat_n")
        top_bat = batting_stats.head(n_bat)
        fig2 = px.bar(top_bat, x="runs", y="player", orientation="h", text="runs",
                      hover_data=["strike_rate", "average"], title="Top Run Scorers")
        fig2.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("### Top 10 Wicket Takers")
        n_bowl = st.slider("How many bowlers to show", 5, 25, 10, key="ov_bowl_n")
        top_bowl = bowling_stats.head(n_bowl)
        fig3 = px.bar(top_bowl, x="wickets", y="player", orientation="h", text="wickets",
                      hover_data=["economy", "overs"], title="Top Wicket Takers",
                      color_discrete_sequence=["#e63946"])
        fig3.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("### Runs by Batting Phase")
        phase_runs = df.groupby("ball_phase", observed=True)["total_runs"].sum().reset_index()
        fig4 = px.pie(phase_runs, names="ball_phase", values="total_runs", hole=0.45)
        st.plotly_chart(fig4, use_container_width=True)
    with col4:
        st.markdown("### Runs per Over (League Average)")
        over_avg = df.groupby("over")["total_runs"].mean().reset_index()
        fig5 = px.area(over_avg, x="over", y="total_runs", title="Average runs scored per over")
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### Chase vs Defend Win Rate")
    chase_stats = pd.DataFrame({
        "Result": ["Batting 1st Won", "Chasing Won", "Tie/No Result"],
        "Count": [
            (match_summary["winner"] == match_summary["first_batting_team"]).sum(),
            (match_summary["chase_successful"] == True).sum(),
            (match_summary["winner"] == "Tie/No Result").sum(),
        ]
    })
    fig6 = px.pie(chase_stats, names="Result", values="Count", title="Bat First vs Chase — who wins more?")
    st.plotly_chart(fig6, use_container_width=True)

# ----------------------------------------------------------------------------
# PAGE: TEAM ANALYSIS
# ----------------------------------------------------------------------------
elif page == "Team Analysis":
    page_header("📊", "Team Analysis", "Phase-wise form and top performers, team by team")

    if team_stats.empty:
        st.warning("No matches found for the current filters.")
    else:
        team = st.selectbox("Select a team", sorted(team_stats["team"].unique()))
        team_row = team_stats[team_stats["team"] == team].iloc[0]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Matches", int(team_row["matches"]))
        c2.metric("Wins", int(team_row["wins"]))
        c3.metric("Losses", int(team_row["losses"]))
        c4.metric("Win %", f"{team_row['win_pct']}%")
        c5.metric("Chase Win %", f"{team_row['chase_win_pct']}%", help="Win % when chasing a target")

        team_deliveries = df[df["batting_team"] == team]
        team_bowl_deliveries = df[df["bowling_team"] == team]

        st.markdown(f"### {team} — Batting Phase Breakdown")
        phase_stats = team_deliveries.groupby("ball_phase", observed=True).agg(
            runs=("total_runs", "sum"), wickets=("is_wicket", "sum"),
            balls=("is_legal_ball", "sum")
        ).reset_index()
        phase_stats["run_rate"] = (phase_stats["runs"] / (phase_stats["balls"] / 6)).round(2)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(phase_stats, x="ball_phase", y="runs", color="ball_phase", text="runs",
                         title=f"{team} — Runs by Phase")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig1b = px.bar(phase_stats, x="ball_phase", y="run_rate", color="ball_phase", text="run_rate",
                            title=f"{team} — Run Rate by Phase")
            st.plotly_chart(fig1b, use_container_width=True)

        st.markdown(f"### {team} — Top Performers")
        col1, col2 = st.columns(2)
        with col1:
            t_bat = batting_stats[batting_stats["player"].isin(team_deliveries["striker"].unique())].head(10)
            st.dataframe(t_bat[["player", "runs", "balls_faced", "strike_rate", "average", "boundary_pct", "fours", "sixes"]],
                         use_container_width=True, hide_index=True)
        with col2:
            t_bowl = bowling_stats[bowling_stats["player"].isin(team_bowl_deliveries["bowler"].unique())].head(10)
            st.dataframe(t_bowl[["player", "wickets", "overs", "economy", "dot_pct"]],
                         use_container_width=True, hide_index=True)

        st.markdown("### All Teams Comparison")
        metric_choice = st.radio("Compare teams by", ["Win % vs Avg Score", "Chase Win % vs Matches"], horizontal=True)
        if metric_choice == "Win % vs Avg Score":
            fig5 = px.scatter(team_stats, x="avg_score", y="win_pct", text="team", size="matches",
                               color="team", color_discrete_map=TEAM_COLORS,
                               title="Average Score vs Win %")
        else:
            fig5 = px.scatter(team_stats, x="matches", y="chase_win_pct", text="team", size="wins",
                               color="team", color_discrete_map=TEAM_COLORS,
                               title="Chase Win % vs Matches Played")
        fig5.update_traces(textposition="top center")
        fig5.update_layout(showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)
        csv_download_button(team_stats, "Download all team stats CSV", "all_team_stats.csv")

# ----------------------------------------------------------------------------
# PAGE: PLAYER STATS
# ----------------------------------------------------------------------------
elif page == "Player Stats":
    page_header("🧑‍🤝‍🧑", "Player Stats", "Leaderboards and phase specialists across the season")

    tab1, tab2, tab3 = st.tabs(["Batting", "Bowling", "Phase Specialists"])

    with tab1:
        min_balls = st.slider("Minimum balls faced", 0, 100, 30)
        filtered = batting_stats[batting_stats["balls_faced"] >= min_balls]
        sort_by = st.selectbox("Sort by", ["runs", "strike_rate", "average", "boundary_pct", "sixes", "fours"], key="bat_sort")
        filtered = filtered.sort_values(sort_by, ascending=False)
        csv_download_button(filtered, "Download batting stats CSV", "batting_stats.csv")
        fig = px.scatter(filtered.head(30), x="strike_rate", y="average", size="runs",
                          hover_name="player", color="boundary_pct",
                          title="Strike Rate vs Average (top 30 by filter, colored by boundary %)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            filtered[["player", "matches", "runs", "balls_faced", "average", "strike_rate",
                      "boundary_pct", "dot_pct", "fours", "sixes"]],
            use_container_width=True, hide_index=True, height=450
        )

    with tab2:
        st.markdown("#### Powerplay & Death Overs Specialists")
        phase_choice = st.selectbox("Phase", ["Powerplay (1-6)", "Middle (7-15)", "Death (16-20)"])
        role = st.radio("Role", ["Batting (by Strike Rate)", "Bowling (by Economy)"], horizontal=True)
        min_balls_phase = st.slider("Minimum balls in this phase", 0, 60, 12)

        if role.startswith("Batting"):
            sub = phase_batting[(phase_batting["ball_phase"] == phase_choice) & (phase_batting["balls"] >= min_balls_phase)]
            sub = sub.sort_values("strike_rate", ascending=False).head(15)
            fig = px.bar(sub, x="strike_rate", y="player", orientation="h", text="strike_rate",
                         title=f"Best Strike Rates — {phase_choice}", hover_data=["runs", "balls"])
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            sub = phase_bowling[(phase_bowling["ball_phase"] == phase_choice) & (phase_bowling["balls"] >= min_balls_phase)]
            sub = sub.sort_values("economy", ascending=True).head(15)
            fig = px.bar(sub, x="economy", y="player", orientation="h", text="economy",
                         title=f"Best Economy — {phase_choice}", hover_data=["wickets", "balls"])
            fig.update_layout(yaxis={"categoryorder": "total descending"})
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        min_overs = st.slider("Minimum overs bowled", 0.0, 20.0, 5.0)
        filtered_b = bowling_stats[bowling_stats["overs"] >= min_overs]
        sort_by_b = st.selectbox("Sort by", ["wickets", "economy", "average", "dot_pct"], key="bowl_sort")
        ascending = sort_by_b == "economy"
        filtered_b = filtered_b.sort_values(sort_by_b, ascending=ascending)
        fig2 = px.scatter(filtered_b.head(30), x="economy", y="wickets", size="overs",
                           hover_name="player", color="dot_pct",
                           title="Economy vs Wickets (top 30 by filter, colored by dot ball %)")
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(
            filtered_b[["player", "matches", "overs", "runs_conceded", "wickets", "economy", "average", "dot_pct"]],
            use_container_width=True, hide_index=True, height=450
        )
        csv_download_button(filtered_b, "Download bowling stats CSV", "bowling_stats.csv")

# ----------------------------------------------------------------------------
# PAGE: PLAYER COMPARISON
# ----------------------------------------------------------------------------
elif page == "Player Comparison":
    page_header("⚖️", "Player Comparison", "Head-to-head profiles, normalized against the league")

    comp_type = st.radio("Compare", ["Batters", "Bowlers"], horizontal=True)

    if comp_type == "Batters":
        players = sorted(batting_stats["player"].unique())
        col1, col2 = st.columns(2)
        p1 = col1.selectbox("Player A", players, index=0)
        p2 = col2.selectbox("Player B", players, index=min(1, len(players) - 1))

        metrics = ["runs", "strike_rate", "average", "boundary_pct", "matches"]
        row1 = batting_stats[batting_stats["player"] == p1][metrics].iloc[0]
        row2 = batting_stats[batting_stats["player"] == p2][metrics].iloc[0]
        maxes = batting_stats[metrics].max()
        norm1 = (row1 / maxes * 100).fillna(0)
        norm2 = (row2 / maxes * 100).fillna(0)

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=norm1.values, theta=metrics, fill="toself", name=p1))
        fig.add_trace(go.Scatterpolar(r=norm2.values, theta=metrics, fill="toself", name=p2))
        fig.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 100]}},
                           title="Normalized comparison (% of league max in current filter)")
        st.plotly_chart(fig, use_container_width=True)

        comp_table = pd.DataFrame({p1: row1, p2: row2})
        st.dataframe(comp_table, use_container_width=True)

        st.markdown("#### Strike Rate by Phase")
        pb = phase_batting[phase_batting["player"].isin([p1, p2])]
        fig2 = px.bar(pb, x="ball_phase", y="strike_rate", color="player", barmode="group",
                      title="Phase-wise Strike Rate")
        st.plotly_chart(fig2, use_container_width=True)

    else:
        players = sorted(bowling_stats["player"].unique())
        col1, col2 = st.columns(2)
        p1 = col1.selectbox("Player A", players, index=0)
        p2 = col2.selectbox("Player B", players, index=min(1, len(players) - 1))

        metrics = ["wickets", "overs", "matches"]
        inv_metrics = ["economy"]
        row1 = bowling_stats[bowling_stats["player"] == p1][metrics + inv_metrics].iloc[0]
        row2 = bowling_stats[bowling_stats["player"] == p2][metrics + inv_metrics].iloc[0]
        maxes = bowling_stats[metrics].max()
        norm1 = (row1[metrics] / maxes * 100).fillna(0)
        norm2 = (row2[metrics] / maxes * 100).fillna(0)
        # invert economy: lower is better -> normalize as (max-val)/max*100
        econ_max = bowling_stats["economy"].max()
        norm1["economy (inverted)"] = (econ_max - row1["economy"]) / econ_max * 100
        norm2["economy (inverted)"] = (econ_max - row2["economy"]) / econ_max * 100

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=norm1.values, theta=norm1.index, fill="toself", name=p1))
        fig.add_trace(go.Scatterpolar(r=norm2.values, theta=norm2.index, fill="toself", name=p2))
        fig.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 100]}},
                           title="Normalized comparison (economy inverted so higher = better)")
        st.plotly_chart(fig, use_container_width=True)

        comp_table = pd.DataFrame({p1: row1, p2: row2})
        st.dataframe(comp_table, use_container_width=True)

        st.markdown("#### Economy by Phase")
        pb = phase_bowling[phase_bowling["player"].isin([p1, p2])]
        fig2 = px.bar(pb, x="ball_phase", y="economy", color="player", barmode="group",
                      title="Phase-wise Economy")
        st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------------------------------
# PAGE: VENUE ANALYSIS
# ----------------------------------------------------------------------------
elif page == "Venue Analysis":
    page_header("🏟️", "Venue Analysis", "Scoring conditions and chase trends by ground")

    if venue_stats.empty:
        st.warning("No matches found for the current filters.")
    else:
        st.dataframe(venue_stats, use_container_width=True, hide_index=True)
        csv_download_button(venue_stats, "Download venue stats CSV", "venue_stats.csv")

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(venue_stats.sort_values("avg_1st_innings_score", ascending=False),
                         x="avg_1st_innings_score", y="venue", orientation="h",
                         title="Average 1st Innings Score by Venue", text="avg_1st_innings_score")
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(venue_stats.sort_values("chase_win_pct", ascending=False),
                          x="chase_win_pct", y="venue", orientation="h",
                          title="Chasing Win % by Venue", text="chase_win_pct",
                          color="chase_win_pct", color_continuous_scale="RdYlGn")
            fig2.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Explore a Venue")
        venue_choice = st.selectbox("Select venue", venue_stats["venue"].tolist())
        v_matches = match_summary[match_summary["venue"] == venue_choice]
        st.dataframe(
            v_matches[["match_no", "date", "team1", "score1", "team2", "score2", "winner"]],
            use_container_width=True, hide_index=True
        )

# ----------------------------------------------------------------------------
# PAGE: MATCH EXPLORER
# ----------------------------------------------------------------------------
elif page == "Match Explorer":
    page_header("🔍", "Match Explorer", "Worm chart, Manhattan chart and wicket timeline for any match")

    if match_summary.empty:
        st.warning("No matches found for the current filters.")
    else:
        ordered = match_summary.sort_values("match_no").reset_index(drop=True)
        match_labels = ordered.apply(
            lambda r: f"#{r['match_no']} — {r['team1']} vs {r['team2']} ({r['date'].strftime('%d %b')})", axis=1
        )
        idx = st.selectbox("Select a match", range(len(ordered)), format_func=lambda i: match_labels.iloc[i])
        m = ordered.iloc[idx]

        st.subheader(f"{m['team1']} vs {m['team2']} — {m['phase']}, {m['venue']}")
        c1, c2 = st.columns(2)
        c1.metric(m["team1"], f"{m['score1']}/{m['wkts1']}")
        c2.metric(m["team2"], f"{m['score2']}/{m['wkts2']}")
        if m["winner"] != "Tie/No Result":
            st.success(f"🏆 **{m['winner']}** won by {m['margin']} runs (aggregate) — "
                       f"{'chasing' if m['winner'] == m['chasing_team'] else 'defending'}")
        else:
            st.info("Match tied / no clear result from data")

        match_df = df[df["match_id"] == m["match_id"]].copy()
        match_df["cum_over"] = match_df.groupby("innings").cumcount() + 1
        match_df["cum_runs"] = match_df.groupby("innings")["total_runs"].cumsum()

        st.markdown("### Worm Chart (Cumulative Runs, wickets marked)")
        fig = go.Figure()
        for inn in sorted(match_df["innings"].unique()):
            sub = match_df[match_df["innings"] == inn]
            team_name = sub["batting_team"].iloc[0]
            fig.add_trace(go.Scatter(x=sub["over"], y=sub["cum_runs"], mode="lines",
                                      name=f"Inn {inn}: {team_name}",
                                      line={"color": TEAM_COLORS.get(team_name)}))
            wkt_balls = sub[sub["is_wicket"] == 1]
            fig.add_trace(go.Scatter(x=wkt_balls["over"], y=wkt_balls["cum_runs"], mode="markers",
                                      marker={"symbol": "x", "size": 10, "color": "black"},
                                      name=f"Wickets ({team_name})", showlegend=True))
        fig.update_layout(xaxis_title="Over", yaxis_title="Cumulative Runs")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Manhattan Chart (Runs per Over)")
        over_runs = match_df.copy()
        over_runs["over_num"] = over_runs["over"].astype(int)
        manhattan = over_runs.groupby(["innings", "over_num"]).agg(
            runs=("total_runs", "sum"), wickets=("is_wicket", "sum")
        ).reset_index()
        fig_m = px.bar(manhattan, x="over_num", y="runs", color="innings", barmode="group",
                       title="Runs scored per over (each innings)", hover_data=["wickets"])
        st.plotly_chart(fig_m, use_container_width=True)

        st.markdown("### Wickets Timeline")
        wkts_df = match_df[match_df["is_wicket"] == 1][
            ["innings", "over", "batting_team", "player_dismissed", "bowler", "wicket_type"]
        ]
        st.dataframe(wkts_df, use_container_width=True, hide_index=True)
        csv_download_button(match_df, "Download this match's ball-by-ball CSV", f"match_{m['match_id']}.csv")

# ----------------------------------------------------------------------------
# PAGE: HEAD-TO-HEAD
# ----------------------------------------------------------------------------
elif page == "Head-to-Head":
    page_header("⚔️", "Head-to-Head Comparison", "Every meeting between two teams this season")

    teams = sorted(team_stats["team"].unique())
    if len(teams) < 2:
        st.warning("Need at least two teams in the current filter to compare.")
    else:
        col1, col2 = st.columns(2)
        team_a = col1.selectbox("Team A", teams, index=0)
        team_b = col2.selectbox("Team B", teams, index=1)

        if team_a == team_b:
            st.warning("Pick two different teams.")
        else:
            h2h = match_summary[
                ((match_summary["team1"] == team_a) & (match_summary["team2"] == team_b)) |
                ((match_summary["team1"] == team_b) & (match_summary["team2"] == team_a))
            ]
            if h2h.empty:
                st.info(f"{team_a} and {team_b} haven't played each other under the current filters.")
            else:
                wins_a = (h2h["winner"] == team_a).sum()
                wins_b = (h2h["winner"] == team_b).sum()
                c1, c2, c3 = st.columns(3)
                c1.metric(f"{team_a} wins", wins_a)
                c2.metric("Matches played", len(h2h))
                c3.metric(f"{team_b} wins", wins_b)

                st.dataframe(
                    h2h[["match_no", "date", "venue", "team1", "score1", "team2", "score2", "winner"]],
                    use_container_width=True, hide_index=True
                )
                csv_download_button(h2h, "Download head-to-head CSV", f"{team_a}_vs_{team_b}.csv")

                fig = px.pie(names=[team_a, team_b], values=[wins_a, wins_b],
                             color=[team_a, team_b], color_discrete_map=TEAM_COLORS,
                             title=f"{team_a} vs {team_b} — Win Share")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### Score Comparison Across Matches")
                melt_rows = []
                for _, r in h2h.iterrows():
                    melt_rows.append({"match_no": r["match_no"], "team": r["team1"], "score": r["score1"]})
                    melt_rows.append({"match_no": r["match_no"], "team": r["team2"], "score": r["score2"]})
                melt_df = pd.DataFrame(melt_rows)
                fig2 = px.line(melt_df, x="match_no", y="score", color="team", markers=True,
                               color_discrete_map=TEAM_COLORS, title="Scores over time")
                st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------------------------------
# PAGE: SEASON INSIGHTS
# ----------------------------------------------------------------------------
elif page == "Insights":
    page_header("💡", "Season Insights", "Auto-generated highlights and patterns from this season's ball-by-ball data")
 
    final_matches = raw_match_summary[raw_match_summary["phase"].str.contains("Final", case=False, na=False)]
    if not final_matches.empty:
        final_match = final_matches.sort_values("match_no").iloc[-1]
        if final_match["winner"] != "Tie/No Result":
            champion = final_match["winner"]
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(242,183,5,0.16), rgba(242,183,5,0.02));
                    border: 1px solid var(--gold); border-left: 5px solid var(--gold);
                    border-radius: 10px; padding: 18px 22px; margin-bottom: 20px;">
                    <div style="color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.75rem;">
                        IPL 2026 Champions
                    </div>
                    <div style="font-family: 'Oswald', sans-serif; font-size: 2rem; color: var(--gold); font-weight: 700; margin-top: 2px;">
                        🏆 {champion}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("🏆 The final was tied / no clear result from the data.")
    else:
        st.info("🏆 No final match found in this dataset.")
 
    top_team_row = team_stats.iloc[0]
    top_scorer = batting_stats.iloc[0]
    top_wkt = bowling_stats.iloc[0]
    highest_score_match = match_summary.loc[
        match_summary[["score1", "score2"]].max(axis=1).idxmax()
    ]
    highest_score_val = max(highest_score_match["score1"], highest_score_match["score2"])
    highest_score_team = (
        highest_score_match["team1"] if highest_score_match["score1"] == highest_score_val
        else highest_score_match["team2"]
    )
    decided = match_summary[match_summary["winner"] != "Tie/No Result"]
    closest_match = decided.loc[decided["margin"].idxmin()] if not decided.empty else None
    total_sixes = int(df["is_boundary6"].sum())
    total_fours = int(df["is_boundary4"].sum())
 
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Most Wins", top_team_row["team"], f"{int(top_team_row['wins'])} wins")
    c2.metric("🏏 Top Run-Scorer", top_scorer["player"], f"{int(top_scorer['runs'])} runs")
    c3.metric("🎯 Top Wicket-Taker", top_wkt["player"], f"{int(top_wkt['wickets'])} wkts")
    c4.metric("💥 Highest Total", highest_score_team, f"{highest_score_val}")
 
    if closest_match is not None:
        st.info(
            f"🔥 **Closest finish:** {closest_match['team1']} vs {closest_match['team2']} "
            f"— won by just {int(closest_match['margin'])} runs"
        )
    st.caption(f"⚡ Season boundary count: **{total_fours:,} fours** · **{total_sixes:,} sixes**")
 
    st.markdown("### Runs & Wickets by Batting Phase")
    phase_summary = df.groupby("ball_phase", observed=True).agg(
        runs=("total_runs", "sum"), wickets=("is_wicket", "sum"),
        sixes=("is_boundary6", "sum"), fours=("is_boundary4", "sum"),
    ).reset_index()
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(phase_summary, x="ball_phase", y="runs", color="ball_phase", text="runs",
                     title="Runs Scored by Phase")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(phase_summary, x="ball_phase", y="wickets", color="ball_phase", text="wickets",
                      title="Wickets Lost by Phase")
        st.plotly_chart(fig2, use_container_width=True)
 
    st.markdown("### Boundary Hitters — Fours vs Sixes")
    top_boundary = batting_stats.sort_values(["sixes", "fours"], ascending=False).head(10)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=top_boundary["player"], y=top_boundary["fours"], name="Fours"))
    fig3.add_trace(go.Bar(x=top_boundary["player"], y=top_boundary["sixes"], name="Sixes"))
    fig3.update_layout(barmode="stack", title="Top 10 Boundary Hitters")
    st.plotly_chart(fig3, use_container_width=True)
 
    st.markdown("### Most Consistent Chasers vs Defenders")
    match_summary_dec = match_summary[match_summary["winner"] != "Tie/No Result"].copy()
    st.dataframe(
        team_stats[["team", "matches", "wins", "losses", "win_pct", "avg_score"]]
        .sort_values("win_pct", ascending=False),
        use_container_width=True, hide_index=True
    )
 
st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit · IPL 2026 ball-by-ball data")