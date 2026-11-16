"""
Royal Insight - Bowling analytics helpers.
Reads the already-computed bowling_scores_full.csv. Same shrinkage and
eligibility rules as batting (n/(n+80), >=40 pressure legal balls), but a
separate metric set (economy, wicket-rate, dot%, boundary-conceded%).
"""
from __future__ import annotations
import pandas as pd
from modules.data_loader import load_bowling_scores, load_deliveries

DISPLAY_COLUMNS = {
    "rank": "Rank",
    "player_name": "Player",
    "bowling_reliability_score": "Reliability Score",
    "pressure_legal_balls_total": "Pressure Legal Balls",
    "pressure_matches_total": "Pressure Matches",
    "pressure_economy": "Pressure Economy",
    "baseline_economy": "Baseline Economy",
    "pressure_wickets": "Pressure Wickets",
    "pressure_balls_per_wkt": "Pressure Balls/Wkt",
    "baseline_balls_per_wkt": "Baseline Balls/Wkt",
    "formats_played": "Format(s)",
    "shrink_factor": "Confidence (0-1)",
}


def get_full_leaderboard() -> pd.DataFrame:
    df = load_bowling_scores().copy()
    df = df.sort_values("bowling_reliability_score", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df


def search_players(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return df
    return df[df["player_name"].str.contains(query, case=False, na=False)]


def filter_leaderboard(df: pd.DataFrame, min_balls: int = 0, formats: list | None = None) -> pd.DataFrame:
    out = df[df["pressure_legal_balls_total"] >= min_balls]
    if formats:
        out = out[out["formats_played"].apply(lambda f: any(fmt in f for fmt in formats))]
    return out


def player_delivery_history(player_id: int) -> pd.DataFrame:
    df = load_deliveries()
    return df[(df["bowler_id"] == player_id) & (df["is_legal_delivery"] | df["is_wide"] | df["is_noball"])]


def phase_breakdown(player_id: int) -> pd.DataFrame:
    hist = player_delivery_history(player_id)
    if hist.empty:
        return pd.DataFrame(columns=["phase", "economy", "balls"])
    legal = hist[hist["is_legal_delivery"]]
    g = legal.groupby("phase").agg(runs=("bowler_conceded_runs", "sum"), balls=("is_legal_delivery", "size")).reset_index()
    g["economy"] = 6 * g["runs"] / g["balls"]
    order = {"Powerplay": 0, "Middle": 1, "Death": 2}
    g["_o"] = g["phase"].map(order)
    return g.sort_values("_o").drop(columns="_o")


def season_trend(player_id: int) -> pd.DataFrame:
    hist = player_delivery_history(player_id)
    hist = hist[hist["is_legal_delivery"]]
    if hist.empty:
        return pd.DataFrame(columns=["season", "pressure_economy", "baseline_economy"])
    rows = []
    for season, g in hist.groupby("season"):
        base_econ = 6 * g["bowler_conceded_runs"].sum() / len(g)
        hp = g[g["pressure_tier"] == "High"]
        hp_econ = (6 * hp["bowler_conceded_runs"].sum() / len(hp)) if len(hp) >= 6 else None
        rows.append({"season": season, "baseline_economy": base_econ, "pressure_economy": hp_econ})
    return pd.DataFrame(rows).sort_values("season")
