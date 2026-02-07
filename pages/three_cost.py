"""Page 3 — Cost Story (main visual narrative)."""
import streamlit as st

from src.data import load_medical_insurance
from src.metrics import charge_percentiles, charges_by_smoker_stats
from src.viz import (
    charges_distribution_percentiles,
    charges_by_smoker_box,
    age_vs_charges_scatter,
    bmi_vs_charges_scatter,
    bmi_vs_charges_by_smoker,
    region_charges_box,
    sex_charges_box,
)


@st.cache_data
def _load_data():
    return load_medical_insurance()


def render():
    st.title("Cost Story")
    st.markdown("A sequential narrative on where costs come from and what drives them.")
    try:
        df = _load_data()
    except Exception as e:
        st.error(str(e))
        return
    percentiles = charge_percentiles(df)
    smoker_stats = charges_by_smoker_stats(df)
    st.subheader("1. A small share of claims drives most cost")
    st.plotly_chart(charges_distribution_percentiles(df, percentiles), use_container_width=True)
    st.markdown(
        "Charges are right-skewed. Percentile markers (P50–P99) show how the long tail extends. "
        "Monitoring the high percentiles helps focus on the cases that drive most cost."
    )
    st.subheader("2. Smoking status dominates high-cost risk")
    st.plotly_chart(charges_by_smoker_box(df), use_container_width=True)
    if not smoker_stats.empty:
        st.dataframe(smoker_stats, use_container_width=True, hide_index=True)
    st.markdown(
        "Smokers show much higher median and mean charges. Relying on averages alone is misleading—"
        "the distribution and median tell a clearer story."
    )
    st.subheader("3. Risk compounds with age, especially for smokers")
    st.plotly_chart(age_vs_charges_scatter(df), use_container_width=True)
    st.markdown("Older age and smoking together associate with higher charges; the trend line and color highlight the effect.")
    st.subheader("4. BMI alone is not the main driver")
    st.plotly_chart(bmi_vs_charges_scatter(df), use_container_width=True)
    st.plotly_chart(bmi_vs_charges_by_smoker(df), use_container_width=True)
    st.markdown("BMI shows a weaker relationship with charges than smoking; the interaction with smoker status adds context.")
    st.subheader("5. Regional and demographic effects are secondary")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(region_charges_box(df), use_container_width=True)
    with col2:
        st.plotly_chart(sex_charges_box(df), use_container_width=True)
    st.markdown("Region and sex show smaller differences than smoking or age; they are secondary in the cost story.")
