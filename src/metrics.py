"""
Computed statistics for KPIs and narrative support.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def kpi_strip(df: pd.DataFrame) -> dict[str, float | int]:
    """Row count, median charges, P95 charges, smoker percentage."""
    out: dict[str, float | int] = {"row_count": len(df)}
    if "charges" in df.columns:
        out["median_charges"] = float(df["charges"].median())
        out["p95_charges"] = float(df["charges"].quantile(0.95))
    else:
        out["median_charges"] = out["p95_charges"] = 0.0
    if "smoker" in df.columns:
        smoker_pct = df["smoker"].astype(str).str.lower().str.strip()
        out["smoker_pct"] = float(100 * (smoker_pct.isin(["yes", "true", "1"]).sum() / len(df)))
    else:
        out["smoker_pct"] = 0.0
    return out


def charge_percentiles(df: pd.DataFrame) -> dict[str, float]:
    """P50, P75, P90, P95, P99 for charges."""
    if "charges" not in df.columns:
        return {}
    s = df["charges"].dropna()
    return {
        "p50": float(s.quantile(0.50)),
        "p75": float(s.quantile(0.75)),
        "p90": float(s.quantile(0.90)),
        "p95": float(s.quantile(0.95)),
        "p99": float(s.quantile(0.99)),
    }


def charges_by_smoker_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Mean and median charges by smoker status."""
    if "smoker" not in df.columns or "charges" not in df.columns:
        return pd.DataFrame()
    g = df.groupby(df["smoker"].astype(str).str.lower().str.strip(), dropna=False)["charges"].agg(
        ["mean", "median", "count"]
    )
    g.columns = ["mean_charges", "median_charges", "count"]
    return g.reset_index()


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summary stats for all numeric columns."""
    num = df.select_dtypes(include=[np.number])
    if num.empty:
        return pd.DataFrame()
    return num.describe().T
