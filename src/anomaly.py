"""
Explainable anomaly flagging: percentile or IQR. Flag, don't delete.
"""
from __future__ import annotations

import pandas as pd


def flag_anomalies_charges(
    df: pd.DataFrame,
    method: str = "percentile",
    percentile: float = 95.0,
    iqr_mult: float = 1.5,
) -> tuple[pd.Series, pd.DataFrame]:
    """
    Flag rows as anomalous based on charges.
    method: "percentile" (e.g. > P95) or "iqr" (above Q3 + iqr_mult * IQR).
    Returns (boolean mask, table of flagged rows with reason).
    """
    if "charges" not in df.columns:
        return pd.Series(False, index=df.index), pd.DataFrame()

    charges = df["charges"].dropna()
    if method == "percentile":
        thresh = charges.quantile(percentile / 100.0)
        mask = df["charges"] > thresh
        reason = f"> P{int(percentile)}"
    else:
        q1, q3 = charges.quantile(0.25), charges.quantile(0.75)
        iqr = q3 - q1
        thresh = q3 + iqr_mult * iqr
        mask = df["charges"] > thresh
        reason = "IQR upper fence"
    mask = mask.fillna(False)

    flagged = df.loc[mask].copy()
    flagged["reason"] = reason
    flagged = flagged.sort_values("charges", ascending=False)
    return mask, flagged


def top_anomalies_table(flagged: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Return top n anomalies with key columns and reason for display."""
    cols = [c for c in ["age", "sex", "bmi", "children", "smoker", "region", "charges", "reason"] if c in flagged.columns]
    return flagged[cols].head(n)
