"""
Royal Insight - Pressure Model (documentation + read-only helpers)
--------------------------------------------------------------------
This module does NOT recompute the pressure score - that was already done
once, carefully, in the original SupeRR Selector analysis, and the result
is shipped in data/processed/deliveries_with_pressure.parquet.

What lives here is:
  1) the exact weights/thresholds used (loaded from pressure_thresholds.json
     so the dashboard can never silently drift from the real values), and
  2) small read-only helper functions that describe / summarise that
     already-computed score for the UI (e.g. breaking down how much each
     component contributed, on average, for a given subset of deliveries).

Formula (fixed, from the original analysis):

    pressure_score = 0.30 * wicket_pressure
                    + 0.20 * phase_weight
                    + 0.35 * situation_pressure
                    + 0.15 * crunch_factor

Tiers (percentile cuts of pressure_score across the whole dataset):
    Low     : below the 60th percentile
    Medium  : 60th - 85th percentile
    High    : top 15% of all deliveries
"""
from __future__ import annotations
import pandas as pd
from modules.data_loader import load_pressure_thresholds

COMPONENT_WEIGHTS = {"wicket": 0.30, "phase": 0.20, "situation": 0.35, "crunch": 0.15}

COMPONENT_LABELS = {
    "wicket_pressure": "Wickets in hand",
    "phase_weight": "Innings phase",
    "situation_pressure": "Chase / par-rate situation",
    "crunch_factor": "Crunch factor (overs elapsed x wickets down)",
}

PHASE_WEIGHTS = {"Powerplay": 0.15, "Middle": 0.45, "Death": 0.85}


def get_thresholds() -> dict:
    """Returns {'q60':..., 'q85':..., 'weights': {...}} exactly as used originally."""
    return load_pressure_thresholds()


def component_contribution_table(df: pd.DataFrame) -> pd.DataFrame:
    """Average (weighted) contribution of each pressure component, for any
    delivery subset the user has filtered to - purely descriptive, uses the
    already-computed component columns, never recomputes them."""
    rows = []
    for col, weight_key in [
        ("wicket_pressure", "wicket"),
        ("phase_weight", "phase"),
        ("situation_pressure", "situation"),
        ("crunch_factor", "crunch"),
    ]:
        if col not in df.columns:
            continue
        avg_raw = df[col].fillna(0).mean()
        weight = COMPONENT_WEIGHTS[weight_key]
        rows.append({
            "Component": COMPONENT_LABELS[col],
            "Weight": weight,
            "Avg. raw value (0-1)": round(avg_raw, 3),
            "Avg. weighted contribution": round(avg_raw * weight, 3),
        })
    return pd.DataFrame(rows)


def explain_delivery(row: pd.Series) -> str:
    """Human-readable explanation of why one delivery got its pressure tier."""
    bits = []
    if pd.notna(row.get("wickets_remaining")):
        bits.append(f"{int(row['wickets_remaining'])} wicket(s) in hand")
    if pd.notna(row.get("phase")):
        bits.append(f"{row['phase']} overs")
    if row.get("innings") == 2 and pd.notna(row.get("required_run_rate")):
        bits.append(
            f"chasing at a required rate of {row['required_run_rate']:.1f} "
            f"vs. a current rate of {row.get('current_run_rate', float('nan')):.1f}"
        )
    elif pd.notna(row.get("par_run_rate")):
        bits.append(
            f"scoring at {row.get('current_run_rate', float('nan')):.1f} vs. a historical par "
            f"rate of {row['par_run_rate']:.1f} for this stage"
        )
    tier = row.get("pressure_tier", "Unknown")
    score = row.get("pressure_score", float("nan"))
    return (
        f"Classified **{tier} pressure** (score {score:.2f}/1.00): "
        + ", ".join(bits) + "."
    )
