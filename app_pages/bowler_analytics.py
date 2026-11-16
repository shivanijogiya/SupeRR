import streamlit as st
import pandas as pd
from modules.bowling_analytics import (
    get_full_leaderboard, search_players, filter_leaderboard, DISPLAY_COLUMNS,
    season_trend, phase_breakdown,
)
from modules.visualizations import pressure_vs_baseline_grouped, scatter_sample_vs_score, trend_line


def render():
    st.markdown("## Bowler Analytics")
    st.caption("Pressure-adjusted bowling reliability - identical methodology and numbers as the final submission.")

    leaderboard = get_full_leaderboard()

    st.markdown("### Top 10 Pressure Bowlers")
    top10 = leaderboard.head(10).rename(columns=DISPLAY_COLUMNS)
    cols = [DISPLAY_COLUMNS[c] for c in DISPLAY_COLUMNS if DISPLAY_COLUMNS[c] in top10.columns]
    st.dataframe(top10[cols], hide_index=True, use_container_width=True)
    st.plotly_chart(
        pressure_vs_baseline_grouped(leaderboard.head(10), "player_name", "pressure_economy",
                                      "baseline_economy", "Top 10: Pressure Economy vs. Baseline Economy",
                                      "Pressure Econ", "Baseline Econ"),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### Complete Bowler Leaderboard")
    f1, f2, f3 = st.columns([2, 1, 1])
    query = f1.text_input("Search player by name", "", key="bowl_search")
    min_balls = f2.number_input("Min. pressure legal balls", min_value=0, value=40, step=10, key="bowl_min_balls")
    sort_by = f3.selectbox("Sort by", ["bowling_reliability_score", "pressure_economy", "pressure_wickets",
                                        "pressure_legal_balls_total"], format_func=lambda c: DISPLAY_COLUMNS.get(c, c))

    filtered = filter_leaderboard(leaderboard, min_balls=min_balls)
    filtered = search_players(filtered, query)
    ascending = sort_by == "pressure_economy"
    filtered = filtered.sort_values(sort_by, ascending=ascending)

    if filtered.empty:
        st.warning("No bowlers match your search/filter. Try loosening the filters.")
    else:
        display = filtered.rename(columns=DISPLAY_COLUMNS)
        cols2 = [DISPLAY_COLUMNS[c] for c in DISPLAY_COLUMNS if DISPLAY_COLUMNS[c] in display.columns]
        st.dataframe(display[cols2], hide_index=True, use_container_width=True, height=420)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("Download this leaderboard as CSV", csv, "bowling_leaderboard.csv", "text/csv")

    st.markdown("### Sample Size vs. Reliability (why shrinkage matters)")
    top10_ids = leaderboard.head(10)["player_id"].tolist()
    st.plotly_chart(
        scatter_sample_vs_score(leaderboard, "pressure_legal_balls_total", "composite_z_raw", "player_name", top10_ids),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### Player Drill-Down")
    player_name = st.selectbox("Select a player to inspect", leaderboard["player_name"].tolist(), key="bowl_drill")
    row = leaderboard[leaderboard["player_name"] == player_name].iloc[0]

    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.metric("Reliability Score", f"{row['bowling_reliability_score']:.3f}")
    pc2.metric("Pressure Economy", f"{row['pressure_economy']:.2f}", f"{row['baseline_economy']-row['pressure_economy']:.2f} cheaper")
    pc3.metric("Pressure Wickets", f"{int(row['pressure_wickets'])}")
    pc4.metric("Sample Confidence", f"{row['shrink_factor']:.2f}")

    dc1, dc2 = st.columns(2)
    with dc1:
        phases = phase_breakdown(int(row["player_id"]))
        if not phases.empty:
            st.plotly_chart(trend_line(phases, "phase", "economy", None, f"{player_name}: Economy by Phase"),
                             use_container_width=True)
    with dc2:
        trend = season_trend(int(row["player_id"]))
        if not trend.empty:
            melted = trend.melt(id_vars="season", value_vars=["pressure_economy", "baseline_economy"],
                                 var_name="type", value_name="economy")
            st.plotly_chart(trend_line(melted, "season", "economy", "type", f"{player_name}: Economy Across Seasons"),
                             use_container_width=True)

    st.markdown("### Compare Multiple Bowlers")
    multi = st.multiselect("Select 2+ bowlers to compare side by side", leaderboard["player_name"].tolist(),
                            default=leaderboard.head(3)["player_name"].tolist(), key="bowl_multi")
    if len(multi) >= 2:
        comp = leaderboard[leaderboard["player_name"].isin(multi)].rename(columns=DISPLAY_COLUMNS)
        cols3 = [DISPLAY_COLUMNS[c] for c in DISPLAY_COLUMNS if DISPLAY_COLUMNS[c] in comp.columns]
        st.dataframe(comp[cols3], hide_index=True, use_container_width=True)
    else:
        st.info("Select at least 2 players above to compare.")
