"""Page 4 — Anomalies: Flag, Don't Delete."""
import streamlit as st

from src.data import load_medical_insurance
from src.anomaly import flag_anomalies_charges, top_anomalies_table
from src.viz import anomaly_scatter, anomaly_histogram_overlay


@st.cache_data
def _load_data():
    return load_medical_insurance()


def render():
    st.title("Anomalies: Flag, Don't Delete")
    st.markdown(
        "We flag unusual patterns using explainable rules (e.g. above P95 or IQR) so they can be "
        "reviewed operationally—not deleted. Retaining anomalies supports auditing and monitoring."
    )
    try:
        df = _load_data()
    except Exception as e:
        st.error(str(e))
        return
    method = st.radio("Anomaly rule", ["percentile", "iqr"], format_func=lambda x: "Above P95 (percentile)" if x == "percentile" else "IQR upper fence", horizontal=True)
    if method == "percentile":
        p = st.slider("Percentile threshold", 90, 99, 95)
        mask, flagged = flag_anomalies_charges(df, method="percentile", percentile=float(p))
    else:
        mask, flagged = flag_anomalies_charges(df, method="iqr", iqr_mult=1.5)
    st.subheader("Scatter: flagged vs typical")
    st.plotly_chart(anomaly_scatter(df, mask, x_col="age", y_col="charges"), use_container_width=True)
    st.subheader("Histogram with anomaly overlay")
    st.plotly_chart(anomaly_histogram_overlay(df, mask, col="charges"), use_container_width=True)
    st.subheader("Sortable table of top anomalies")
    top = top_anomalies_table(flagged, n=25)
    st.dataframe(top, use_container_width=True, hide_index=True)
    st.markdown(
        "**Why we keep anomalies:** Deleting them would bias summaries and hide operational risk. "
        "Insurers can use these flags for manual review, case management, or monitoring dashboards."
    )
