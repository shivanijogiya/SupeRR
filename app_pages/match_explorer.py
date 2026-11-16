import streamlit as st
import pandas as pd
from modules.data_loader import load_deliveries


def render():
    st.markdown("## Match & Delivery Explorer")
    st.caption("Drill into the underlying ball-by-ball data behind every number in this dashboard.")

    df = load_deliveries()

    st.markdown("### Filters")
    c1, c2, c3, c4 = st.columns(4)
    comp = c1.multiselect("Competition", sorted(df["comp_name"].dropna().unique().tolist()))
    season = c2.multiselect("Season", sorted(df["season"].dropna().unique().tolist()))
    team = c3.multiselect(
        "Batting team (by ID)", sorted(df["batting_team_id"].dropna().unique().tolist())
    )
    tier = c4.multiselect("Pressure Category", ["Low", "Medium", "High"])

    c5, c6, c7 = st.columns(3)
    match_id = c5.text_input("Match ID (exact)", "")
    player = c6.text_input("Player name contains (batter or bowler)", "")
    innings = c7.multiselect("Innings", sorted(df["innings"].dropna().unique().tolist()))

    out = df
    if comp:
        out = out[out["comp_name"].isin(comp)]
    if season:
        out = out[out["season"].isin(season)]
    if team:
        out = out[out["batting_team_id"].isin(team)]
    if tier:
        out = out[out["pressure_tier"].isin(tier)]
    if match_id.strip():
        try:
            out = out[out["match_id"] == int(match_id.strip())]
        except ValueError:
            st.warning("Match ID must be numeric.")
    if player.strip():
        out = out[
            out["striker_name"].str.contains(player, case=False, na=False)
            | out["bowler_name"].str.contains(player, case=False, na=False)
        ]
    if innings:
        out = out[out["innings"].isin(innings)]

    st.caption(f"{len(out):,} deliveries match your filters (of {len(df):,} total).")

    display_cols = [
        "match_id", "comp_name", "season", "innings", "over_ball_num", "innings_ball_num",
        "striker_name", "bowler_name", "runs", "extras_type", "is_wicket", "dismissal_type",
        "phase", "wickets_remaining", "balls_remaining", "required_run_rate", "current_run_rate",
        "pressure_score", "pressure_tier",
    ]
    display_cols = [c for c in display_cols if c in out.columns]

    if out.empty:
        st.warning("No deliveries match your filters. Try widening your search.")
    else:
        st.dataframe(out[display_cols].head(2000), hide_index=True, use_container_width=True, height=440)
        if len(out) > 2000:
            st.caption("Showing the first 2,000 matching rows. Narrow your filters or download the full result below.")
        csv = out[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered deliveries as CSV", csv, "delivery_explorer_export.csv", "text/csv")

        st.markdown("### How does performance change by situation here?")
        if out["striker_name"].nunique() == 1 or player.strip():
            agg = out.groupby("pressure_tier").agg(
                balls=("runs", "size"), runs=("runs", "sum"), wkts=("is_wicket", "sum")
            )
            if not agg.empty:
                agg["strike_rate"] = 100 * agg["runs"] / agg["balls"]
                st.dataframe(agg, use_container_width=True)
        else:
            st.caption("Narrow the filters to a single player to see a situation-by-situation breakdown.")
