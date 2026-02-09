"""Data Quality & Integrity."""
import streamlit as st
import pandas as pd

from src.data import load_medical_insurance, get_validation_report
from src.metrics import kpi_strip
from src.viz import charges_boxplot, charges_histogram, numeric_boxplots


@st.cache_data
def _load_data():
    return load_medical_insurance()


@st.cache_data
def _kpis(df):
    return kpi_strip(df)


def render():
    st.title("Data Quality & Integrity")

    # Neutral metric card style (no colored edges/glow) for this page only
    st.markdown(
        """
        <style>
        /* Key Metrics: neutral cards on Data Quality page */
        [data-testid="stMetric"] {
            background-color: #ffffff !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
            border: 1px solid rgba(0,0,0,0.06) !important;
            border-left: none !important;
            border-radius: 8px;
            padding: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = _load_data()
        kpis = _kpis(df)
    except Exception as e:
        st.error(str(e))
        return

    st.subheader("Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Row count", f"{kpis['row_count']:,}")
    c2.metric("Median charges", f"${kpis['median_charges']:,.0f}")
    c3.metric("95th Percentile charges", f"${kpis['p95_charges']:,.0f}")
    c4.metric("Smoker %", f"{kpis['smoker_pct']:.1f}%")

    report = get_validation_report(df)
    st.subheader("Columns and Data types")
    st.dataframe(pd.DataFrame(report["schema"].items(), columns=["Column", "Dtype"]), use_container_width=True, hide_index=True)
    st.subheader("Missing values")
    missing = report["missing"]
    if any(missing.values()):
        st.dataframe(pd.DataFrame(missing.items(), columns=["Column", "Missing count"]), use_container_width=True, hide_index=True)
    else:
        st.info("No missing values in the dataset.")
    st.subheader("Distinct category values")
    for col, vals in report["category_values"].items():
        st.write(f"**{col}:** {sorted(set(vals))}")
    st.subheader("Invalid range checks")
    st.caption("Count of values outside valid ranges (age 1–100, BMI 10–60, children 0–20, charges > 0):")
    ir = report["invalid_ranges"]
    st.dataframe(pd.DataFrame(ir.items(), columns=["Column", "Invalid count"]), use_container_width=True, hide_index=True)
    st.subheader("Charges: spread and distribution")
    st.plotly_chart(charges_boxplot(df), use_container_width=True)
    st.markdown("*Takeaway: Charges have a long right tail, a few high-cost cases pull the average up.*")
    st.plotly_chart(charges_histogram(df), use_container_width=True)
    st.markdown("*Takeaway: Most claims cluster at lower charges, a minority drive very high cost.*")
    st.subheader("Other features")
    st.plotly_chart(numeric_boxplots(df), use_container_width=True)
    st.markdown("*Takeaway: Age, BMI, and children fall within expected ranges in this dataset, no data quality issues are indicated.*")


if __name__ in ("__main__", "__page__"):
    render()
