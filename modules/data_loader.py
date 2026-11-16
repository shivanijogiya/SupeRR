"""
Royal Insight - Data Loader
----------------------------
Loads the raw supporting tables and the pre-computed, pressure-enriched
delivery data and player rankings that power every page of the dashboard.

All heavy data (the 199k-row ball-by-ball feed with the Pressure Score
already attached, and the final batting/bowling reliability rankings) was
produced once by the original SupeRR Selector analysis pipeline and is
shipped here as ready-to-read files under data/processed/. The dashboard
NEVER recomputes the pressure model or the rankings from scratch - it reads
and visualises the exact same numbers that were used for the Round 1
submission, so every figure shown here is traceable back to that analysis.
"""
from __future__ import annotations

import json
import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROC_DIR = os.path.join(DATA_DIR, "processed")


@st.cache_data(show_spinner=False)
def load_deliveries() -> pd.DataFrame:
    """The full pressure-enriched ball-by-ball dataset (one row per delivery)."""
    path = os.path.join(PROC_DIR, "deliveries_with_pressure.parquet")
    df = pd.read_parquet(path)
    return df


@st.cache_data(show_spinner=False)
def load_matches() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))


@st.cache_data(show_spinner=False)
def load_competitions() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))


@st.cache_data(show_spinner=False)
def load_teams() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "teams.csv"))


@st.cache_data(show_spinner=False)
def load_playing_eleven() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))


@st.cache_data(show_spinner=False)
def load_player_mapping() -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))


@st.cache_data(show_spinner=False)
def load_batting_scores() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROC_DIR, "batting_scores_full.csv"))


@st.cache_data(show_spinner=False)
def load_bowling_scores() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROC_DIR, "bowling_scores_full.csv"))


@st.cache_data(show_spinner=False)
def load_batting_top10() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROC_DIR, "batting_top10.csv"))


@st.cache_data(show_spinner=False)
def load_bowling_top10() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROC_DIR, "bowling_top10.csv"))


@st.cache_data(show_spinner=False)
def load_batting_ci() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROC_DIR, "batting_bootstrap_ci.csv"))


@st.cache_data(show_spinner=False)
def load_bowling_ci() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROC_DIR, "bowling_bootstrap_ci.csv"))


@st.cache_data(show_spinner=False)
def load_validation_summary() -> dict:
    with open(os.path.join(PROC_DIR, "validation_summary.json")) as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_pressure_thresholds() -> dict:
    with open(os.path.join(PROC_DIR, "pressure_thresholds.json")) as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_audit_report() -> dict:
    with open(os.path.join(PROC_DIR, "audit_report.json")) as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_innings_totals() -> pd.DataFrame:
    return pd.read_csv(os.path.join(PROC_DIR, "innings_totals.csv"))


def rankings_workbook_path() -> str:
    return os.path.join(BASE_DIR, "outputs", "player_rankings.xlsx")


@st.cache_data(show_spinner=False)
def last_refreshed() -> str:
    path = os.path.join(PROC_DIR, "deliveries_with_pressure.parquet")
    ts = os.path.getmtime(path)
    return pd.Timestamp(ts, unit="s").strftime("%d %b %Y")
