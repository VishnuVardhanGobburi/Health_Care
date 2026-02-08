"""Context & Big Idea."""
import streamlit as st

from src.data import load_medical_insurance
from src.metrics import kpi_strip


@st.cache_data
def _load_data():
    return load_medical_insurance()


@st.cache_data
def _kpis(df):
    return kpi_strip(df)


def render():
    st.title("Insurance Claim Risk: Context & Objectives")
    try:
        df = _load_data()
        kpis = _kpis(df)
    except Exception as e:
        st.error(f"Could not load data. {e}")
        return
    st.subheader("Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Row count", f"{kpis['row_count']:,}")
    c2.metric("Median charges", f"${kpis['median_charges']:,.0f}")
    c3.metric("95th Percentile charges", f"${kpis['p95_charges']:,.0f}")
    c4.metric("Smoker %", f"{kpis['smoker_pct']:.1f}%")

    st.subheader("ProblemStatement:")
    st.markdown(
        "Insurance claim data is highly skewed. Most claims are relatively low cost, while a small number of claims account for disproportionately high charges. " \
        "Relying on averages often hides this imbalance, making it difficult to analyse to understand where risk truly concentrates or how to prioritize review efforts."
    )
    st.subheader("What this project does")
    st.markdown("This project provides a structured, end-to-end view of insurance claim risk by combining data quality checks, exploratory analysis, anomaly flagging, predictive modeling, and an AI-driven FAQ assistant into a single, coherent workflow.")
    st.subheader("Who this is for")
    st.markdown("This project is designed for:")
    st.markdown("- **Claims analysts** who need to identify and review high-risk claims efficiently.")
    st.markdown("- **Business stakeholders and managers** who rely on analytics to translate raw claims data into decisions.")
    st.markdown("- **Non-technical users and policy stakeholders** who need quick, reliable answers to insurance-related questions through an AI-driven, document-grounded FAQ assistant")
    st.subheader("What each page does")
    st.markdown("- **Data Quality & Integrity:** Ensures the data is trustworthy by validating ranges, categories, and distributions before analysis." )
    st.markdown("- **Drivers of Insurance Claim Costs:** Explores how claim charges vary across smoking status, age, BMI, region, and demographics using distribution-focused visuals." )
    st.markdown("- **High-Charge Claim Review:** Flags unusually high claims using percentile- and IQR-based rules to support targeted review." )
    st.markdown("- **High-Charge Risk Estimator:** Uses interpretable machine-learning models to estimate high-charge risk, compare trade-offs, and explain which factors drive predictions." )
    st.markdown("- **Insurance FAQ Assistant (AI-driven):** Provides a document-grounded conversational interface to answer insurance-related questions with reduced hallucination risk." )
    st.markdown("- **Accuracy & Hallucination Testing**: Evaluates AI responses to ensure reliability and document-grounded answers." )


if __name__ in ("__main__", "__page__"):
    render()
