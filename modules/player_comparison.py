"""
Royal Insight - Player comparison helpers (batters vs batters, bowlers vs bowlers).
"""
from __future__ import annotations
import pandas as pd


def normalise_0_100(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series([50] * len(series), index=series.index)
    norm = (series - lo) / (hi - lo) * 100
    return norm if higher_is_better else 100 - norm


def batting_radar_values(row: pd.Series, pool: pd.DataFrame) -> list:
    cats = {
        "Pressure SR": ("pressure_strike_rate", True),
        "SR Uplift": ("sr_vs_baseline_pct", True),
        "Low Dismissal Risk": ("pressure_dismissal_rate", False),
        "Reliability Score": ("batting_reliability_score", True),
        "Sample Confidence": ("shrink_factor", True),
    }
    values = []
    for _, (col, higher) in cats.items():
        norm = normalise_0_100(pool[col], higher_is_better=higher)
        values.append(round(norm.loc[row.name], 1))
    return values


def bowling_radar_values(row: pd.Series, pool: pd.DataFrame) -> list:
    cats = {
        "Low Economy": ("pressure_economy", False),
        "Wicket Threat": ("pressure_wickets", True),
        "Economy Uplift": ("baseline_economy", True),  # baseline - pressure handled via pool below
        "Reliability Score": ("bowling_reliability_score", True),
        "Sample Confidence": ("shrink_factor", True),
    }
    values = []
    for label, (col, higher) in cats.items():
        if label == "Economy Uplift":
            uplift = pool["baseline_economy"] - pool["pressure_economy"]
            norm = normalise_0_100(uplift, higher_is_better=True)
        else:
            norm = normalise_0_100(pool[col], higher_is_better=higher)
        values.append(round(norm.loc[row.name], 1))
    return values


BATTING_RADAR_CATEGORIES = ["Pressure SR", "SR Uplift", "Low Dismissal Risk", "Reliability Score", "Sample Confidence"]
BOWLING_RADAR_CATEGORIES = ["Low Economy", "Wicket Threat", "Economy Uplift", "Reliability Score", "Sample Confidence"]
