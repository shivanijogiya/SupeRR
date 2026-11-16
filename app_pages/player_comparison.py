import streamlit as st
import pandas as pd
from modules.batting_analytics import get_full_leaderboard as get_batters
from modules.bowling_analytics import get_full_leaderboard as get_bowlers
from modules.player_comparison import (
    batting_radar_values, bowling_radar_values, BATTING_RADAR_CATEGORIES, BOWLING_RADAR_CATEGORIES,
)
from modules.visualizations import radar_chart


def render():
    st.markdown("## Player Comparison")
    st.caption("Build a side-by-side comparison of two or more batters, or two or more bowlers.")

    discipline = st.radio("Discipline", ["Batters", "Bowlers"], horizontal=True)

    if discipline == "Batters":
        pool = get_batters()
        pool_idx = pool.set_index(pool.index)
        default = pool.head(2)["player_name"].tolist()
        chosen = st.multiselect("Select batters to compare (2 or more)", pool["player_name"].tolist(), default=default)
        if len(chosen) < 2:
            st.info("Select at least 2 batters.")
            return
        sub = pool[pool["player_name"].isin(chosen)]
        series = {}
        for _, row in sub.iterrows():
            series[row["player_name"]] = batting_radar_values(row, pool)
        st.plotly_chart(radar_chart(BATTING_RADAR_CATEGORIES, series, "Batting Comparison (0-100 normalised)"),
                         use_container_width=True)
        table_cols = ["player_name", "batting_reliability_score", "pressure_strike_rate", "baseline_strike_rate",
                      "sr_vs_baseline_pct", "pressure_dismissal_rate", "pressure_balls_total", "shrink_factor",
                      "formats_played"]
        st.dataframe(sub[table_cols], hide_index=True, use_container_width=True)
        csv = sub[table_cols].to_csv(index=False).encode("utf-8")
        st.download_button("Download comparison as CSV", csv, "batter_comparison.csv", "text/csv")

    else:
        pool = get_bowlers()
        default = pool.head(2)["player_name"].tolist()
        chosen = st.multiselect("Select bowlers to compare (2 or more)", pool["player_name"].tolist(), default=default)
        if len(chosen) < 2:
            st.info("Select at least 2 bowlers.")
            return
        sub = pool[pool["player_name"].isin(chosen)]
        series = {}
        for _, row in sub.iterrows():
            series[row["player_name"]] = bowling_radar_values(row, pool)
        st.plotly_chart(radar_chart(BOWLING_RADAR_CATEGORIES, series, "Bowling Comparison (0-100 normalised)"),
                         use_container_width=True)
        table_cols = ["player_name", "bowling_reliability_score", "pressure_economy", "baseline_economy",
                      "pressure_wickets", "pressure_legal_balls_total", "shrink_factor", "formats_played"]
        st.dataframe(sub[table_cols], hide_index=True, use_container_width=True)
        csv = sub[table_cols].to_csv(index=False).encode("utf-8")
        st.download_button("Download comparison as CSV", csv, "bowler_comparison.csv", "text/csv")

    st.caption(
        "Radar values are min-max normalised to 0-100 across all eligible players for readability only; "
        "the underlying Reliability Scores and raw metrics in the table above are the real, unscaled figures."
    )
