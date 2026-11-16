import streamlit as st
import plotly.graph_objects as go
from modules.auction_intelligence import squad_fit_table, players_for_role, fit_matrix, ALL_ROLES
from modules.visualizations import NAVY2, PINK, CARD_BG, TEXT, GRID


def _fit_matrix_heatmap():
    mat = fit_matrix()
    fig = go.Figure(go.Heatmap(
        z=mat.values, x=mat.columns, y=mat.index,
        colorscale=[[0, "#2A2A4A"], [1, PINK]], showscale=False,
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG, font=dict(color=TEXT, size=11),
        title="Rajasthan Royals IPL 2027 - Shortlist Squad-Fit Matrix",
        height=560, margin=dict(l=140, r=20, t=50, b=120),
        xaxis=dict(tickangle=-40, gridcolor=GRID), yaxis=dict(gridcolor=GRID, autorange="reversed"),
    )
    return fig


def render():
    st.markdown("## Rajasthan Royals - Auction Intelligence")
    st.caption(
        "Translates the pressure-reliability rankings into squad-building insight. "
        "All figures below are evidenced skill fit only - not auction prices, retentions, or availability, "
        "none of which were supplied in the data pack."
    )

    table = squad_fit_table()

    st.markdown("### Filter by Squad Role")
    role = st.selectbox("Squad-role need", ["All roles"] + ALL_ROLES)
    shown = table if role == "All roles" else players_for_role(role)

    if shown.empty:
        st.warning("No shortlisted players map to that role.")
    else:
        bat_shown = shown[shown["Discipline"] == "Batter"].sort_values("Rank")
        bowl_shown = shown[shown["Discipline"] == "Bowler"].sort_values("Rank")

        if not bat_shown.empty:
            st.markdown("#### Recommended Batters")
            for _, r in bat_shown.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    c1.markdown(f"**#{r['Rank']} {r['Player']}**")
                    c1.metric("Reliability Score", f"{r['Reliability Score']:.3f}")
                    c2.markdown(f"**Roles:** {r['Roles']}")
                    c2.write(r["Why recommended"])

        if not bowl_shown.empty:
            st.markdown("#### Recommended Bowlers")
            for _, r in bowl_shown.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    c1.markdown(f"**#{r['Rank']} {r['Player']}**")
                    c1.metric("Reliability Score", f"{r['Reliability Score']:.3f}")
                    c2.markdown(f"**Roles:** {r['Roles']}")
                    c2.write(r["Why recommended"])

    st.markdown("---")
    st.plotly_chart(_fit_matrix_heatmap(), use_container_width=True)

    st.markdown("### Full Shortlist Table")
    st.dataframe(table, hide_index=True, use_container_width=True)
    csv = table.to_csv(index=False).encode("utf-8")
    st.download_button("Download auction shortlist as CSV", csv, "rr_auction_shortlist.csv", "text/csv")

    st.info(
        "**Data-supported finding:** each player's role tags and 'why recommended' text are derived directly "
        "from their pressure-vs-baseline delta and phase-level profile in the underlying analysis.\n\n"
        "**Strategic interpretation:** the grouping of these players into RR's specific squad needs "
        "(finishing depth, death pace, middle-overs spin) is an analyst judgement call layered on top of "
        "the data, not itself a statistical output."
    )
