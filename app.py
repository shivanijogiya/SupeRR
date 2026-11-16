"""
ROYAL INSIGHT - Pressure Performance & Auction Intelligence Platform
======================================================================
Main Streamlit entry point. Run with:  streamlit run app.py
(or just double-click run.bat on Windows, which does this for you)

This file only handles page config, theming, and sidebar navigation.
All real logic lives in modules/ (data + calculations) and pages/
(one render() function per dashboard page).
"""
import os
import base64
import streamlit as st

from app_pages import (
    overview, pressure_analysis, batter_analytics, bowler_analytics,
    player_comparison, auction_intelligence, match_explorer, methodology,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Royal Insight | Pressure Performance & Auction Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css():
    css_path = os.path.join(BASE_DIR, "assets", "custom.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def logo_b64() -> str | None:
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


PAGES = {
    "Executive Overview": overview,
    "Pressure Analysis": pressure_analysis,
    "Batter Analytics": batter_analytics,
    "Bowler Analytics": bowler_analytics,
    "Player Comparison": player_comparison,
    "RR Auction Intelligence": auction_intelligence,
    "Match & Delivery Explorer": match_explorer,
    "Methodology & Transparency": methodology,
}


def main():
    load_css()

    with st.sidebar:
        b64 = logo_b64()
        if b64:
            st.markdown(
                f"""
                <div style="text-align:center; padding: 8px 0 4px 0;">
                    <img src="data:image/png;base64,{b64}" width="72">
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(
            """
            <div style="text-align:center; margin-bottom: 18px;">
                <div style="font-size:1.1rem; font-weight:800; color:#EDEDF5; letter-spacing:1px;">ROYAL INSIGHT</div>
                <div style="font-size:0.72rem; color:#C9A24B; letter-spacing:0.5px;">PRESSURE PERFORMANCE &amp;<br>AUCTION INTELLIGENCE</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        choice = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
        st.markdown("---")
        st.caption("SupeRR Selector Season 2 - Round 1")
        st.caption("Rajasthan Royals IPL 2027 Auction Strategy")

    st.markdown(
        f"""
        <div class="ri-header">
            <div class="ri-crest">RI</div>
            <div>
                <div class="ri-title">ROYAL INSIGHT</div>
                <div class="ri-subtitle">PRESSURE PERFORMANCE &amp; AUCTION INTELLIGENCE PLATFORM</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    PAGES[choice].render()

    st.markdown(
        '<div class="ri-footer">Royal Insight is an analytical tool built on the SupeRR Selector Season 2 '
        'data pack. All figures are statistical findings from supplied historical data, not predictions, '
        'auction prices, or guarantees of player availability.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
