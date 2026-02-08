"""
Healthcare Insurance Claims Analytics — Streamlit app.
Story-driven Plotly visualizations + FAQ RAG chatbot.
"""
import streamlit as st

st.set_page_config(
    page_title="Healthcare Insurance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto",
)

# Global typography: smaller, dashboard-like headings across all pages
st.markdown(
    """
    <style>
    /* Page title (st.title) */
    h1 { font-size: 1.8rem; margin-bottom: 0.4rem; }

    /* Section headers (st.header) */
    h2 { font-size: 1.3rem; margin-top: 1.2rem; margin-bottom: 0.35rem; }

    /* Subheaders (st.subheader) */
    h3 { font-size: 1.1rem; margin-top: 0.8rem; margin-bottom: 0.3rem; }

    /* Optional: body text readability */
    p  { font-size: 0.95rem; line-height: 1.5; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Insurance Analytics")
st.sidebar.markdown("Story-driven insights and FAQ AI assistant.")

pages = [
    st.Page("pages/context_big_idea.py", title="Context & Objectives"),
    st.Page("pages/cost_story.py", title="Drivers of Insurance Claim Costs"),
    st.Page("pages/anomalies_flag_dont_delete.py", title="High-Charge Claim Review"),
    st.Page("pages/high_charge_risk_estimator.py", title="High-Charge Risk Estimator"),
    st.Page("pages/data_quality_integrity.py", title="Data Quality & Integrity"),
    st.Page("pages/insurance_faq_assistant.py", title="Insurance FAQ Assistant"),
    st.Page("pages/accuracy_hallucination_testing.py", title="Accuracy & Hallucination Testing"),
]
pg = st.navigation(pages)
pg.run()
