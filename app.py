"""
Healthcare Insurance Claims Analytics — Streamlit app.
Story-driven Plotly visualizations + FAQ RAG chatbot.
"""
import streamlit as st

st.set_page_config(
    page_title="Healthcare Insurance Analytics",
    layout="wide",
    initial_sidebar_state="auto",
)

# Global typography: consistent font and lighter weight for titles/headers/subheaders on all pages
st.markdown(
    """
    <style>
    /* Shared font for headings */
    h1, h2, h3, .section-title, .subheader, .card h4 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    }

    /* Page title (st.title) */
    h1 { font-size: 1.45rem; font-weight: 500; margin-bottom: 0.5rem; }

    /* Section headers (st.header) */
    h2 { font-size: 1.15rem; font-weight: 500; margin-top: 1.2rem; margin-bottom: 0.35rem; }

    /* Subheaders (st.subheader) */
    h3 { font-size: 1rem; font-weight: 500; margin-top: 0.8rem; margin-bottom: 0.3rem; }

    /* Body text */
    p { font-size: 0.95rem; line-height: 1.5; }

    /* Sidebar title */
    [data-testid="stSidebar"] h1 { font-size: 1.25rem; font-weight: 500; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Insurance Analytics")
st.sidebar.markdown("Story-driven insights and FAQ AI assistant.")

pages = [
    st.Page("pages/introduction.py", title="Introduction"),
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
