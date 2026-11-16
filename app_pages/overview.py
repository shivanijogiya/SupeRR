import streamlit as st
import pandas as pd
from modules.data_loader import (
    load_deliveries, load_matches, load_batting_top10, load_bowling_top10,
    load_audit_report, last_refreshed,
)
from modules.visualizations import (
    kpi_card_html, pressure_tier_pie, pressure_by_phase_bar, leaderboard_bar,
)


def render():
    st.markdown("## Executive Overview")
    st.caption("A one-page summary of the scale of the analysis and the headline findings.")

    deliveries = load_deliveries()
    matches = load_matches()
    bat_top10 = load_batting_top10()
    bowl_top10 = load_bowling_top10()
    audit = load_audit_report()

    total_matches = deliveries["match_id"].nunique()
    total_deliveries = len(deliveries)
    unique_batters = deliveries["striker_id"].nunique()
    unique_bowlers = deliveries["bowler_id"].nunique()
    high_pressure = int((deliveries["pressure_tier"] == "High").sum())
    n_comps = deliveries["comp_name"].nunique() if "comp_name" in deliveries.columns else "-"
    n_seasons = deliveries["season"].nunique()

    kpis = [
        ("Matches Analysed", f"{total_matches:,}", "IPL + T20I, 2022 onward"),
        ("Deliveries Analysed", f"{total_deliveries:,}", "legal + illegal balls"),
        ("Unique Batters", f"{unique_batters:,}", "faced >=1 ball"),
        ("Unique Bowlers", f"{unique_bowlers:,}", "bowled >=1 ball"),
        ("High-Pressure Deliveries", f"{high_pressure:,}", "top 15% by Pressure Score"),
        ("Competitions / Seasons", f"{n_comps} / {n_seasons}", "labelled, never pooled unfairly"),
    ]
    cols = st.columns(3)
    for i, (label, value, sub) in enumerate(kpis):
        with cols[i % 3]:
            st.markdown(kpi_card_html(label, value, sub), unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.plotly_chart(pressure_tier_pie(deliveries), use_container_width=True)
    with c2:
        st.plotly_chart(pressure_by_phase_bar(deliveries), use_container_width=True)

    st.markdown("### Top Performers Under Pressure")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Top 5 Batters**")
        top5b = bat_top10.head(5)[["rank", "player_name", "batting_reliability_score", "pressure_strike_rate"]]
        top5b.columns = ["Rank", "Player", "Reliability Score", "Pressure SR"]
        st.dataframe(top5b, hide_index=True, use_container_width=True)
    with t2:
        st.markdown("**Top 5 Bowlers**")
        top5w = bowl_top10.head(5)[["rank", "player_name", "bowling_reliability_score", "pressure_economy"]]
        top5w.columns = ["Rank", "Player", "Reliability Score", "Pressure Economy"]
        st.dataframe(top5w, hide_index=True, use_container_width=True)

    st.markdown("### Season-wise Coverage")
    season_counts = deliveries.drop_duplicates("match_id")["season"].value_counts().sort_index()
    st.bar_chart(season_counts, color="#E4007C")

    st.markdown("---")
    st.caption(
        f"Data source: SupeRR Selector Season 2 data pack (IPL + T20I ball-by-ball, 2022+). "
        f"{audit.get('abandoned_matches_excluded', 0)} abandoned/no-result matches excluded. "
        f"Analysis last refreshed: {last_refreshed()}."
    )
