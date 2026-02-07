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

# Sidebar navigation
st.sidebar.title("📊 Insurance Analytics")
st.sidebar.markdown("Story-driven insights and FAQ assistant.")
page = st.sidebar.radio(
    "Go to",
    [
        "1. Context & Big Idea",
        "2. Data Quality & Integrity",
        "3. Cost Story",
        "4. Anomalies: Flag, Don't Delete",
        "5. Insurance FAQ Assistant",
        "6. Accuracy & Hallucination Testing",
    ],
    label_visibility="collapsed",
)

# Route to page modules
PAGES = {
    "1. Context & Big Idea": "pages.one_context",
    "2. Data Quality & Integrity": "pages.two_quality",
    "3. Cost Story": "pages.three_cost",
    "4. Anomalies: Flag, Don't Delete": "pages.four_anomaly",
    "5. Insurance FAQ Assistant": "pages.five_chatbot",
    "6. Accuracy & Hallucination Testing": "pages.six_testing",
}


def main():
    mod_name = PAGES.get(page, "pages.one_context")
    import importlib
    mod = importlib.import_module(mod_name)
    mod.render()


if __name__ == "__main__":
    main()
