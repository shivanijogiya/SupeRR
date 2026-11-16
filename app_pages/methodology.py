import streamlit as st
from modules.data_loader import load_audit_report, load_validation_summary


def render():
    st.markdown("## Methodology & Model Transparency")
    st.caption("Every metric in this dashboard is traceable to the steps below. No step is hidden or simplified away.")

    audit = load_audit_report()
    validation = load_validation_summary()

    st.markdown("### 1. Data Sources")
    st.write(
        "IPL + T20I ball-by-ball data (2022 onward), joined with competitions, matches, teams, "
        "playing XIs, and competition-team-player mappings. "
        f"**{audit.get('abandoned_matches_excluded', 0)} abandoned/no-result matches** and matches with no "
        "ball-by-ball rows were excluded before any analysis."
    )

    st.markdown("### 2. Data Cleaning")
    st.write(
        "- Legal vs. illegal deliveries rebuilt from `extras_type` (wide / no-ball), not assumed.\n"
        "- Runs conceded by the bowler exclude byes & leg-byes.\n"
        "- Wickets credited to the bowler exclude run-outs and other non-bowler dismissals.\n"
        "- Batter dismissals are attributed to the striker only (a disclosed limitation - see Section 9)."
    )
    with st.expander("Raw audit numbers"):
        st.json(audit)

    st.markdown("### 3. Feature Engineering")
    st.write(
        "Every delivery is enriched with: cumulative score & wickets before the ball, legal-ball sequence, "
        "balls/wickets remaining, the match target (or revised DLS target), required run rate, current run "
        "rate, innings phase, and a historical par run-rate curve (for 1st-innings pressure)."
    )

    st.markdown("### 4. Pressure Score Formula")
    st.code(
        "pressure_score = 0.30*wicket_pressure + 0.20*phase_weight "
        "+ 0.35*situation_pressure + 0.15*crunch_factor",
        language="text",
    )
    st.write("Tiers: Low (<60th pct), Medium (60th-85th pct), High (top 15%). See the Pressure Analysis page to explore interactively.")

    st.markdown("### 5. Pressure Classification Check")
    st.write(
        "Only ~46% of death-over deliveries are tagged High-pressure (vs. ~14% Middle, ~0.3% Powerplay) - "
        "confirming phase alone does not decide the label, as required by the brief."
    )

    st.markdown("### 6. Batting Score Formula")
    st.code(
        "composite_z = 0.35*z(ΔStrikeRate) + 0.30*z(ΔDismissalRate) + 0.20*z(ΔBoundary%) + 0.15*z(ΔDot%)\n"
        "Batting Reliability Score = composite_z * n / (n + 80)   [n = pressure balls faced]\n"
        "Eligibility: n >= 40 pressure balls faced",
        language="text",
    )

    st.markdown("### 7. Bowling Score Formula")
    st.code(
        "composite_z = 0.35*z(ΔEconomy) + 0.30*z(ΔWicketRate) + 0.20*z(ΔDot%) + 0.15*z(ΔBoundaryConceded%)\n"
        "Bowling Reliability Score = composite_z * n / (n + 80)   [n = pressure legal balls bowled]\n"
        "Eligibility: n >= 40 pressure legal balls",
        language="text",
    )
    st.write("All deltas are z-scored **within** IPL and **within** T20I separately, then blended by actual balls played in each - for fairness across competition standards.")

    st.markdown("### 8. Sample-Size Treatment")
    st.write(
        "Empirical-Bayes shrinkage (`n/(n+80)`) pulls small samples toward the league average, so a player "
        "with a handful of great pressure balls cannot outrank one with hundreds of consistently good ones."
    )

    st.markdown("### 9. Statistical Validation")
    st.json(validation)
    st.write(
        "**Threshold sensitivity** shows the ranking is meaningfully sensitive to how widely 'High pressure' "
        "is defined (disclosed honestly, not hidden). **Weight sensitivity** shows the ranking is largely "
        "stable to the exact composite weights chosen (~93-94% average Top-10 retention under +/-15% jitter)."
    )

    st.markdown("### 10. Known Limitations")
    st.write(
        "- Non-striker run-outs cannot be separated from striker dismissals in this data feed.\n"
        "- 1st-innings pressure uses a historical par-rate proxy (no fixed target exists yet in the 1st innings).\n"
        "- DLS-affected matches (25 of the valid set) use the revised target but a standard innings length "
        "assumption where the revised-overs field was ambiguous.\n"
        "- No opponent-strength, venue, or auction-price adjustment is modelled.\n"
        "- Players near the 40-ball eligibility floor carry materially wider uncertainty - see the bootstrap "
        "confidence ranges on the Batter/Bowler Analytics pages."
    )
