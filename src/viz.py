"""
Plotly figure functions for story-driven healthcare insurance visualizations.
Takeaway-driven titles, minimal clutter, annotations. No pie/donut.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# Consistent layout defaults: minimal gridlines, clear fonts
LAYOUT_DEFAULTS = dict(
    font=dict(size=12, family="sans-serif"),
    margin=dict(l=60, r=40, t=60, b=50),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.08)", zeroline=False),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.08)", zeroline=False),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
)


def _apply_layout(fig: go.Figure, title: str, yaxis_title: str | None = None, xaxis_title: str | None = None) -> None:
    fig.update_layout(title=dict(text=title, x=0.5, xanchor="center"), **LAYOUT_DEFAULTS)
    if yaxis_title:
        fig.update_yaxes(title_text=yaxis_title)
    if xaxis_title:
        fig.update_xaxes(title_text=xaxis_title)


# ---------- Phase 1: Data quality ----------


def charges_boxplot(df: pd.DataFrame) -> go.Figure:
    """Boxplot of charges — spread and outliers."""
    fig = go.Figure(go.Box(y=df["charges"].dropna(), name="Charges", line_color="rgb(31, 119, 180)"))
    fig.update_layout(
        title=dict(text="", x=0.5, xanchor="center"),
        yaxis_title="Charges (USD)",
        **LAYOUT_DEFAULTS,
    )
    return fig


def charges_histogram(df: pd.DataFrame) -> go.Figure:
    """Distribution of charges with minimal styling."""
    fig = go.Figure(go.Histogram(x=df["charges"].dropna(), nbinsx=50, marker_color="rgb(31, 119, 180)"))
    _apply_layout(fig, "", "Count", "Charges (USD)")
    return fig


def numeric_boxplots(df: pd.DataFrame) -> go.Figure:
    """Combined boxplots for age, bmi, children (not charges — that's separate)."""
    cols = [c for c in ["age", "bmi", "children"] if c in df.columns]
    if not cols:
        return go.Figure()
    fig = go.Figure()
    for c in cols:
        fig.add_trace(go.Box(y=df[c].dropna(), name=c.replace("_", " ").title()))
    fig.update_layout(
        title=dict(text="", x=0.5, xanchor="center"),
        yaxis_title="Value",
        **LAYOUT_DEFAULTS,
    )
    return fig


# ---------- Phase 2: Cost story ----------


def _percentile_display_label(key: str) -> str:
    """Convert p50 -> 50th Percentile, p95 -> 95th Percentile, etc."""
    if key.startswith("p") and key[1:].isdigit():
        return f"{key[1:]}th Percentile"
    return key


def charges_distribution_percentiles(
    df: pd.DataFrame, percentiles: dict[str, float]
) -> go.Figure:
    """Charges distribution with 50th–99th Percentile markers."""
    fig = go.Figure(go.Histogram(x=df["charges"].dropna(), nbinsx=60, marker_color="rgb(31, 119, 180)", showlegend=False))
    for label, val in percentiles.items():
        fig.add_vline(x=val, line_dash="dash", line_color="gray", annotation_text=_percentile_display_label(label))
    _apply_layout(
        fig,
        "",
        "Count",
        "Charges (USD)",
    )
    return fig


def charges_by_smoker_box(df: pd.DataFrame) -> go.Figure:
    """Charges by smoker status (box)."""
    df = df.copy()
    df["smoker_label"] = df["smoker"].astype(str).str.lower().str.strip().map(
        lambda x: "Smoker" if x in ("yes", "true", "1") else "Non-smoker"
    )
    fig = px.box(df, x="smoker_label", y="charges", color="smoker_label", points="outliers")
    fig.update_layout(
        title=dict(
            text="",
            x=0.5,
            xanchor="center",
        ),
        xaxis_title="",
        yaxis_title="Charges (USD)",
        **LAYOUT_DEFAULTS,
    )
    fig.update_traces(showlegend=False)
    return fig


def age_vs_charges_scatter(df: pd.DataFrame) -> go.Figure:
    """Age vs charges, colored by smoker (sparingly)."""
    df = df.copy()
    df["Smoker"] = df["smoker"].astype(str).str.lower().str.strip().map(
        lambda x: "Yes" if x in ("yes", "true", "1") else "No"
    )
    fig = px.scatter(
        df, x="age", y="charges", color="Smoker",
        color_discrete_map={"Yes": "rgb(214, 39, 40)", "No": "rgba(31, 119, 180, 0.6)"},
        trendline="ols", trendline_scope="overall",
    )
    fig.update_traces(marker=dict(size=6, opacity=0.7))
    _apply_layout(
        fig,
        "",
        "Charges (USD)",
        "Age",
    )
    return fig


def bmi_vs_charges_scatter(df: pd.DataFrame) -> go.Figure:
    """BMI vs charges."""
    fig = px.scatter(df, x="bmi", y="charges", trendline="ols", opacity=0.7)
    fig.update_traces(marker=dict(size=6, color="rgb(31, 119, 180)"))
    _apply_layout(
        fig,
        "BMI vs charges",
        "Charges (USD)",
        "BMI",
    )
    return fig


def bmi_vs_charges_by_smoker(df: pd.DataFrame) -> go.Figure:
    """BMI vs charges"""
    df = df.copy()
    df["Smoker"] = df["smoker"].astype(str).str.lower().str.strip().map(
        lambda x: "Smoker" if x in ("yes", "true", "1") else "Non-smoker"
    )
    fig = px.scatter(
        df, x="bmi", y="charges", color="Smoker",
        color_discrete_map={"Smoker": "rgb(214, 39, 40)", "Non-smoker": "rgb(31, 119, 180)"},
        trendline="ols",
    )
    fig.update_traces(marker=dict(size=5, opacity=0.6))
    _apply_layout(
        fig,
        "BMI vs charges by smoking status",
        "Charges (USD)",
        "BMI",
    )
    return fig


def region_charges_box(df: pd.DataFrame) -> go.Figure:
    """Region vs charges (de-emphasized)."""
    fig = px.box(df, x="region", y="charges", points="outliers")
    fig.update_traces(marker_color="rgb(31, 119, 180)")
    _apply_layout(
        fig,
        "Region vs charges",
        "Charges (USD)",
        "Region",
    )
    return fig


def sex_charges_box(df: pd.DataFrame) -> go.Figure:
    """Sex vs charges (de-emphasized)."""
    fig = px.box(df, x="sex", y="charges", points="outliers")
    fig.update_traces(marker_color="rgb(31, 119, 180)")
    _apply_layout(
        fig,
        "Sex vs charges",
        "Charges (USD)",
        "Sex",
    )
    return fig


def children_charges_box(df: pd.DataFrame) -> go.Figure:
    """Box plot of charges by number of children (discrete category)."""
    df = df.copy()
    df["children_cat"] = df["children"].astype(int).astype(str)
    fig = px.box(df, x="children_cat", y="charges", points="outliers")
    fig.update_traces(marker_color="rgb(31, 119, 180)")
    fig.update_layout(
        title=dict(text="Charges by number of children", x=0.5, xanchor="center"),
        xaxis_title="Number of children",
        yaxis_title="Charges (USD)",
        **LAYOUT_DEFAULTS,
    )
    return fig


# ---------- Phase 3: Anomalies ----------


def anomaly_scatter(
    df: pd.DataFrame,
    anomaly_mask: pd.Series,
    x_col: str = "age",
    y_col: str = "charges",
) -> go.Figure:
    """Scatter with anomalies highlighted."""
    df = df.copy()
    df["_anomaly"] = anomaly_mask
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df.loc[~df["_anomaly"], x_col],
            y=df.loc[~df["_anomaly"], y_col],
            mode="markers",
            name="Typical",
            marker=dict(size=6, color="rgba(31, 119, 180, 0.6)"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df.loc[df["_anomaly"], x_col],
            y=df.loc[df["_anomaly"], y_col],
            mode="markers",
            name="Flagged (anomaly)",
            marker=dict(size=8, color="rgb(214, 39, 40)", symbol="x"),
        )
    )
    _apply_layout(
        fig,
        "Flagged high-cost cases: review, don't delete",
        yaxis_title="Charges (USD)",
        xaxis_title=x_col.replace("_", " ").title(),
    )
    return fig


def anomaly_histogram_overlay(
    df: pd.DataFrame,
    anomaly_mask: pd.Series,
    col: str = "charges",
) -> go.Figure:
    """Histogram with anomaly overlay (separate trace for flagged)."""
    typical = df.loc[~anomaly_mask, col].dropna()
    anom = df.loc[anomaly_mask, col].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=typical, name="Typical", marker_color="rgb(31, 119, 180)", nbinsx=40))
    fig.add_trace(go.Histogram(x=anom, name="Flagged", marker_color="rgb(214, 39, 40)", nbinsx=40))
    fig.update_layout(barmode="overlay")
    _apply_layout(
        fig,
        "High-cost tail: anomalies sit in the right tail of charges",
        "Count",
        "Charges (USD)",
    )
    fig.update_traces(opacity=0.7)
    return fig
