import streamlit as st
import pandas as pd
from modules.data_loader import load_deliveries
from modules.pressure_model import get_thresholds, component_contribution_table, explain_delivery
from modules.visualizations import pressure_score_histogram, pressure_by_phase_bar, pressure_tier_pie


def render():
    st.markdown("## Pressure Analysis")
    st.caption("The exact pressure methodology used to generate the final rankings - explore it interactively.")

    deliveries = load_deliveries()
    thresholds = get_thresholds()

    with st.expander("How the Pressure Score is built (click to expand)", expanded=False):
        st.markdown(
            """
**Pressure Score (0-1), identical for batter and bowler on the same ball:**

```
pressure_score = 0.30 x wicket_pressure
               + 0.20 x phase_weight
               + 0.35 x situation_pressure   (chase gap/RRR, or 1st-innings par-rate deficit)
               + 0.15 x crunch_factor        (overs elapsed x wickets down)
```

**Tiers** (percentile of this score across the whole dataset):
- **Low** — below the 60th percentile
- **Medium** — 60th-85th percentile
- **High** — top 15% of all deliveries

No match outcome (winner, margin, final score) is ever used to build this score - every input
is knowable the instant the ball is bowled.
            """
        )

    st.markdown("### Filters")
    fc1, fc2, fc3, fc4 = st.columns(4)
    seasons = sorted(deliveries["season"].dropna().unique().tolist())
    comp_types = sorted(deliveries["competition_type"].dropna().unique().tolist())
    phases = ["Powerplay", "Middle", "Death"]
    tiers = ["Low", "Medium", "High"]

    sel_seasons = fc1.multiselect("Season", seasons, default=[])
    sel_comp = fc2.multiselect("Competition", comp_types, default=[])
    sel_phase = fc3.multiselect("Innings Phase", phases, default=[])
    sel_tier = fc4.multiselect("Pressure Category", tiers, default=[])

    df = deliveries
    if sel_seasons:
        df = df[df["season"].isin(sel_seasons)]
    if sel_comp:
        df = df[df["competition_type"].isin(sel_comp)]
    if sel_phase:
        df = df[df["phase"].isin(sel_phase)]
    if sel_tier:
        df = df[df["pressure_tier"].isin(sel_tier)]

    if df.empty:
        st.warning("No deliveries match the selected filters. Try widening your selection.")
        return

    st.caption(f"{len(df):,} deliveries match the current filters (of {len(deliveries):,} total).")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(pressure_score_histogram(df, thresholds["q60"], thresholds["q85"]), use_container_width=True)
    with c2:
        st.plotly_chart(pressure_tier_pie(df), use_container_width=True)

    st.plotly_chart(pressure_by_phase_bar(df), use_container_width=True)

    st.markdown("### What's driving the Pressure Score here?")
    st.dataframe(component_contribution_table(df), hide_index=True, use_container_width=True)

    st.markdown("### Inspect an individual delivery")
    sample = df.sample(min(500, len(df)), random_state=1)
    options = sample.apply(
        lambda r: f"Match {r['match_id']} | Inn {int(r['innings'])} | Over {int(r['legal_balls_before'])//6 + 1} | "
                  f"{r.get('striker_name','?')} vs {r.get('bowler_name','?')}",
        axis=1,
    )
    choice = st.selectbox("Pick a delivery to see why it was classified that way", options.tolist())
    if choice:
        idx = options.tolist().index(choice)
        row = sample.iloc[idx]
        st.info(explain_delivery(row))
        detail_cols = ["match_id", "innings", "phase", "wickets_remaining", "balls_remaining",
                        "required_run_rate", "current_run_rate", "pressure_score", "pressure_tier"]
        detail = row[[c for c in detail_cols if c in row.index]].astype(str).to_frame("Value")
        st.dataframe(detail, use_container_width=True)

    csv = df.head(5000).to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered deliveries (CSV, up to 5,000 rows)", csv, "filtered_deliveries.csv", "text/csv")
