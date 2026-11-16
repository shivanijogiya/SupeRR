"""
Royal Insight - Batting analytics helpers.
Reads the already-computed batting_scores_full.csv (same file behind the
final Excel rankings) and provides filtering / search utilities for the UI.
Eligibility and scoring are exactly as produced by the original pipeline:
    Batting Reliability Score = composite_z x (n / (n + 80)), n = pressure balls faced
    Eligibility floor: n >= 40 pressure balls faced.
"""
from __future__ import annotations
import pandas as pd
from modules.data_loader import load_batting_scores, load_deliveries

DISPLAY_COLUMNS = {
    "rank": "Rank",
    "player_name": "Player",
    "batting_reliability_score": "Reliability Score",
    "pressure_balls_total": "Pressure Balls",
    "pressure_innings_total": "Pressure Innings",
    "pressure_strike_rate": "Pressure SR",
    "baseline_strike_rate": "Baseline SR",
    "sr_vs_baseline_pct": "SR Change (%)",
    "pressure_dismissal_rate": "Pressure Dismissal Rate",
    "baseline_dismissal_rate": "Baseline Dismissal Rate",
    "formats_played": "Format(s)",
    "shrink_factor": "Confidence (0-1)",
}


def get_full_leaderboard() -> pd.DataFrame:
    df = load_batting_scores().copy()
    df = df.sort_values("batting_reliability_score", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)
    return df


def search_players(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return df
    return df[df["player_name"].str.contains(query, case=False, na=False)]


def filter_leaderboard(df: pd.DataFrame, min_balls: int = 0, formats: list | None = None) -> pd.DataFrame:
    out = df[df["pressure_balls_total"] >= min_balls]
    if formats:
        out = out[out["formats_played"].apply(lambda f: any(fmt in f for fmt in formats))]
    return out


def player_delivery_history(player_id: int) -> pd.DataFrame:
    """All balls faced by this batter, for drill-down / season trend charts."""
    df = load_deliveries()
    return df[(df["striker_id"] == player_id) & (df["ball_faced_by_batter"])]


def season_trend(player_id: int) -> pd.DataFrame:
    hist = player_delivery_history(player_id)
    if hist.empty:
        return pd.DataFrame(columns=["season", "pressure_strike_rate", "baseline_strike_rate"])
    rows = []
    for season, g in hist.groupby("season"):
        base_sr = g["batter_runs"].mean() * 100
        hp = g[g["pressure_tier"] == "High"]
        hp_sr = hp["batter_runs"].mean() * 100 if len(hp) >= 6 else None
        rows.append({"season": season, "baseline_strike_rate": base_sr, "pressure_strike_rate": hp_sr})
    return pd.DataFrame(rows).sort_values("season")


def phase_breakdown(player_id: int) -> pd.DataFrame:
    hist = player_delivery_history(player_id)
    if hist.empty:
        return pd.DataFrame(columns=["phase", "strike_rate", "balls"])
    g = hist.groupby("phase").agg(runs=("batter_runs", "sum"), balls=("batter_runs", "size")).reset_index()
    g["strike_rate"] = 100 * g["runs"] / g["balls"]
    order = {"Powerplay": 0, "Middle": 1, "Death": 2}
    g["_o"] = g["phase"].map(order)
    return g.sort_values("_o").drop(columns="_o")
