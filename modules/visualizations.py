"""
Royal Insight - Shared Plotly visual theme and chart builders.
All charts in the app go through this module so the look stays consistent.
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

NAVY = "#13132B"
NAVY2 = "#1D1D40"
PINK = "#E4007C"
PINK_LT = "#FF7FB8"
GOLD = "#C9A24B"
GREY = "#9797AC"
CARD_BG = "#1A1A38"
GRID = "#2B2B4A"
TEXT = "#EDEDF5"

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="Segoe UI, Arial", color=TEXT, size=13),
        title=dict(font=dict(size=16, color=TEXT)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID),
        margin=dict(l=40, r=20, t=50, b=40),
        colorway=[PINK, NAVY2, GOLD, PINK_LT, GREY],
    )
)


def _apply(fig: go.Figure, height=420) -> go.Figure:
    fig.update_layout(template=PLOTLY_TEMPLATE, height=height)
    return fig


def pressure_tier_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["pressure_tier"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=["#3A3A5C", PINK_LT, PINK]),
        textinfo="label+percent",
    ))
    fig.update_layout(title="Pressure Tier Mix")
    return _apply(fig, height=380)


def pressure_score_histogram(df: pd.DataFrame, q60: float, q85: float) -> go.Figure:
    fig = px.histogram(df, x="pressure_score", nbins=50, color_discrete_sequence=[NAVY2])
    fig.add_vline(x=q60, line_dash="dash", line_color=GOLD, annotation_text="Medium cut")
    fig.add_vline(x=q85, line_dash="dash", line_color=PINK, annotation_text="High cut")
    fig.update_layout(title="Pressure Score Distribution", xaxis_title="Pressure score (0-1)", yaxis_title="Deliveries")
    return _apply(fig)


def pressure_by_phase_bar(df: pd.DataFrame) -> go.Figure:
    ct = pd.crosstab(df["phase"], df["pressure_tier"], normalize="index").reindex(["Powerplay", "Middle", "Death"]) * 100
    fig = go.Figure()
    colors = {"Low": "#3A3A5C", "Medium": PINK_LT, "High": PINK}
    for tier in ["Low", "Medium", "High"]:
        if tier in ct.columns:
            fig.add_bar(name=tier, x=ct.index, y=ct[tier], marker_color=colors[tier])
    fig.update_layout(barmode="stack", title="Pressure Tier Mix by Innings Phase", yaxis_title="% of deliveries")
    return _apply(fig)


def leaderboard_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str, color=PINK) -> go.Figure:
    d = df.sort_values(x_col)
    fig = go.Figure(go.Bar(x=d[x_col], y=d[y_col], orientation="h", marker_color=color))
    fig.update_layout(title=title, height=max(380, 34 * len(d)))
    return _apply(fig, height=max(380, 34 * len(d)))


def pressure_vs_baseline_grouped(df: pd.DataFrame, name_col: str, pressure_col: str, baseline_col: str,
                                  title: str, pressure_label="Pressure", baseline_label="Baseline") -> go.Figure:
    d = df.sort_values(pressure_col)
    fig = go.Figure()
    fig.add_bar(name=pressure_label, y=d[name_col], x=d[pressure_col], orientation="h", marker_color=PINK)
    fig.add_bar(name=baseline_label, y=d[name_col], x=d[baseline_col], orientation="h", marker_color=NAVY2)
    fig.update_layout(barmode="group", title=title, height=max(380, 50 * len(d)))
    return _apply(fig, height=max(380, 50 * len(d)))


def scatter_sample_vs_score(df: pd.DataFrame, x_col: str, y_col: str, name_col: str, highlight_ids=None,
                             id_col="player_id", title="Pressure performance vs sample size") -> go.Figure:
    highlight_ids = highlight_ids or []
    colors = [PINK if pid in highlight_ids else GREY for pid in df[id_col]]
    sizes = [11 if pid in highlight_ids else 7 for pid in df[id_col]]
    fig = go.Figure(go.Scatter(
        x=df[x_col], y=df[y_col], mode="markers", marker=dict(color=colors, size=sizes, line=dict(width=0)),
        text=df[name_col], hovertemplate="%{text}<br>Balls: %{x}<br>Score: %{y:.2f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=GRID)
    fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col)
    return _apply(fig)


def radar_chart(categories: list, series: dict, title="Comparison") -> go.Figure:
    fig = go.Figure()
    palette = [PINK, GOLD, PINK_LT, "#6BC5B8"]
    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Scatterpolar(r=values + values[:1], theta=categories + categories[:1],
                                       fill="toself", name=name, line_color=palette[i % len(palette)]))
    fig.update_layout(
        polar=dict(bgcolor=CARD_BG, radialaxis=dict(visible=True, gridcolor=GRID, color=TEXT)),
        title=title, showlegend=True,
    )
    return _apply(fig, height=460)


def trend_line(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None, title: str) -> go.Figure:
    if color_col:
        fig = px.line(df, x=x_col, y=y_col, color=color_col, markers=True,
                       color_discrete_sequence=[PINK, NAVY2, GOLD, PINK_LT])
    else:
        fig = px.line(df, x=x_col, y=y_col, markers=True, color_discrete_sequence=[PINK])
    fig.update_layout(title=title)
    return _apply(fig)


def kpi_card_html(label: str, value: str, sub: str = "") -> str:
    return f"""
    <div class="ri-kpi">
        <div class="ri-kpi-value">{value}</div>
        <div class="ri-kpi-label">{label}</div>
        <div class="ri-kpi-sub">{sub}</div>
    </div>
    """
