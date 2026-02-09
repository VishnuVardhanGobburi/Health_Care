import streamlit as st
import os

# Path to welcome image (same folder as app when run from project root)
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Images")
WELCOME_IMAGE = os.path.join(IMAGES_DIR, "welcome.png")


def render():
    # Page-specific styles to match the welcome design
    st.markdown(
        """
        <style>
        /* Hide default Streamlit padding for full-bleed feel */
        .intro-block-container {
            max-width: 900px;
            margin: 0 auto 2rem;
            text-align: center;
        }
        .intro-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #374151;
            margin-bottom: 0.25rem;
            letter-spacing: -0.02em;
        }
        .intro-subtitle {
            font-size: 1.35rem;
            font-weight: 500;
            color: #4b5563;
            margin-bottom: 1rem;
        }
        .intro-author {
            font-size: 1.1rem;
            font-weight: 500;
            color: #2563eb;
            margin-bottom: 2.5rem;
        }
        /* Subtle light background */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #fafbfc 0%, #ffffff 30%, #ffffff 100%);
        }
        /* What each page does cards */
        .intro-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 28px;
            height: 100%;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06), inset 0 0 0 1px rgba(0,0,0,0.04);
            border-left: 6px solid #4f46e5;
        }
        .intro-card h4 { font-size: 1rem; font-weight: 500; margin: 0 0 8px 0; }
        .intro-card p { font-size: 0.9rem; line-height: 1.4; margin: 0; white-space: normal; }
        .intro-subheader { font-size: 1.15rem; font-weight: 500; margin: 6px 0 2px 0; }
        /* Image: ~48% viewport so cards fit without scroll */
        div[data-testid="stImage"] {
            height: 48vh; min-height: 280px;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 0 !important; padding-bottom: 0 !important;
        }
        div[data-testid="stImage"] img {
            height: 48vh; min-height: 280px;
            width: auto; max-width: 100%; object-fit: contain;
        }
        /* Tighten main content so image + cards fit in viewport */
        section.main .block-container { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; max-width: 100%; }
        /* Remove gap between image block and next block */
        div[data-testid="stImage"] { margin-bottom: 0 !important; }
        section.main [data-testid="stVerticalBlock"] { gap: 0.25rem !important; }
        /* Cards section: compact */
        .intro-cards-section { min-height: 0; }
        .intro-card { margin-bottom: 10px !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


    if os.path.isfile(WELCOME_IMAGE):
        st.image(WELCOME_IMAGE, use_container_width=True)
    else:
        st.info("Welcome graphic not found. Add `Images/welcome.png` to match the design.")

    # What each page does (under the image) — ~25% of page
    st.markdown('<div class="intro-cards-section"><div class="intro-subheader">What each page does</div>', unsafe_allow_html=True)
    row1 = st.columns(3)
    row2 = st.columns(3)
    pages = [
        ("Data Quality & Integrity", "Ensures clean, trustworthy claim data before analysis"),
        ("Drivers of Insurance Claim Costs", "Explores how demographics and smoking status impact costs"),
        ("High-Charge Claim Review", "Flags unusually expensive claims for investigation"),
        ("High-Charge Risk Estimator", "Predicts high-cost risk with ML models"),
        ("Insurance FAQ Assistant (AI)", "Answers insurance questions using verified documents"),
        ("Accuracy & Hallucination Testing", "Validates AI outputs for reliability and correctness"),
    ]
    for col, (title, desc) in zip(row1 + row2, pages):
        with col:
            st.markdown(
                f'<div class="intro-card"><h4>{title}</h4><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ in ("__main__", "__page__"):
    render()
