"""Data Quality & Integrity."""
import streamlit as st
import pandas as pd

from src.data import load_medical_insurance, get_validation_report
from src.viz import charges_boxplot, charges_histogram, numeric_boxplots


@st.cache_data
def _load_data():
    return load_medical_insurance()


def render():
    st.title("Data Quality & Integrity")
    try:
        df = _load_data()
    except Exception as e:
        st.error(str(e))
        return
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
