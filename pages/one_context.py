"""Page 1 — Context & Big Idea."""
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
    st.title("Context & Big Idea")
    st.markdown(
        "Healthcare insurance costs are hard to interpret: premiums, deductibles, and claim amounts "
        "vary by demographics, behavior, and region. This app shows how to read the data with clarity "
        "and use it for better decisions—without overwhelming you with charts."
    )
    st.markdown("**Big idea:** A small share of high-cost claims drives most spending; smoking and age are the main risk levers.")
    st.markdown("What you will learn:")
    st.markdown(
        "- **Data trust:** How we validate and check data quality before any analysis  \n"
        "- **Cost story:** Where costs concentrate and why averages mislead  \n"
        "- **Anomalies:** How we flag unusual patterns for review instead of deleting them  \n"
        "- **FAQ assistant:** A document-grounded chatbot for insurance and policy questions  \n"
        "- **Responsible AI:** How we test for accuracy and reduce hallucinations"
    )
    try:
        df = _load_data()
        kpis = _kpis(df)
    except Exception as e:
        st.error(f"Could not load data. {e}")
        return
    st.subheader("Key metrics at a glance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Row count", f"{kpis['row_count']:,}")
    c2.metric("Median charges", f"${kpis['median_charges']:,.0f}")
    c3.metric("P95 charges", f"${kpis['p95_charges']:,.0f}")
    c4.metric("Smoker %", f"{kpis['smoker_pct']:.1f}%")
