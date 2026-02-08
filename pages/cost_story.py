"""Cost Story (main visual narrative)."""
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
    children_charges_box,
)


@st.cache_data
def _load_data():
    return load_medical_insurance()


def render():
    st.title("Drivers of Insurance Claim Costs")
    try:
        df = _load_data()
    except Exception as e:
        st.error(str(e))
        return
    percentiles = charge_percentiles(df)
    smoker_stats = charges_by_smoker_stats(df)

    analysis_choice = st.selectbox(
        "Explore what drives insurance claim charges 👇",
        [
            "What Do Most Claim Charges Look Like?",
            "How Does Smoking Show Up in Claim Charges?",
            "How Do Claim Charges Change with Age?",
            "Where Does BMI Fit into Claim Charges?",
            "Do Region and Demographics Make a Difference?"
        ]
    )

    if analysis_choice == "What Do Most Claim Charges Look Like?":
        st.subheader("A small share of claims drives most cost")
        st.plotly_chart(charges_distribution_percentiles(df, percentiles), use_container_width=True)
        st.markdown(
            "Charges are right-skewed. Percentile markers (50th–99th Percentile) show how the long tail extends. "
            "Which tells most insurance claims have relatively low charges, while a small number of claims exhibit very high charge amounts."
        )
    elif analysis_choice == "How Does Smoking Show Up in Claim Charges?":
        st.subheader("Smoking status dominates high-cost risk")
        st.plotly_chart(charges_by_smoker_box(df), use_container_width=True)
        if not smoker_stats.empty:
            st.dataframe(smoker_stats, use_container_width=True, hide_index=True)
        st.markdown(
            "Smoking status is associated to higher claim charges, mainly because a group of smoker claims reaches much higher cost levels."
        )
    elif analysis_choice == "How Do Claim Charges Change with Age?":
        st.subheader("Risk compounds with age, especially for smokers")
        st.plotly_chart(age_vs_charges_scatter(df), use_container_width=True)
        st.markdown("Claim charges increase with age for both groups, but the increase is stronger among smokers.")
    elif analysis_choice == "Where Does BMI Fit into Claim Charges?":
        st.subheader("BMI alone is not the main driver")
        st.plotly_chart(bmi_vs_charges_scatter(df), use_container_width=True)
        st.plotly_chart(bmi_vs_charges_by_smoker(df), use_container_width=True)
        st.markdown("BMI shows a limited relationship with claim charges on its own, but among smokers, higher BMI is associated with more charges.")
    elif analysis_choice == "Do Region and Demographics Make a Difference?":
        st.subheader("Regional and demographic effects are secondary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(region_charges_box(df), use_container_width=True)
        with col2:
            st.plotly_chart(sex_charges_box(df), use_container_width=True)
        with col3:
            st.plotly_chart(children_charges_box(df), use_container_width=True)
        st.markdown("Regional, sex-based, and family-size (number of children) differences in claim charges are modest, especially when compared to the stronger effects of smoking status and age.")


if __name__ in ("__main__", "__page__"):
    render()
