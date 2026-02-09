"""Context & Big Idea."""
import streamlit as st

# =========================================================
# STYLES (colored edges + same layout)
# =========================================================
st.markdown("""
<style>
/* Section headers - same font/weight as global app headings */
.section-title{
  font-size: 1.45rem;
  font-weight: 500;
  margin: 8px 0 24px 0;
  letter-spacing: -0.4px;
}
.subheader {
  font-size: 1.15rem;
  font-weight: 500;
  margin: 26px 0 18px 0;
}

/* Shared card */
.card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px 18px;
  margin-bottom: 28px;          /* row gap */
  height: 100%;

  /* base shadow + subtle edge line */
  box-shadow:
    0 6px 20px rgba(0,0,0,0.06),
    inset 0 0 0 1px rgba(0,0,0,0.04);

  /* colored edge (default indigo) */
  border-left: 6px solid #4f46e5;
}

/* Card text - aligned with subheader weight/size */
.card h4 {
  font-size: 1rem;
  font-weight: 500;
  margin: 0 0 8px 0;
}
.card p {
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
  white-space: nowrap;          /* 1-line */
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Metric cards */
.metric-label{
  font-size: 0.85rem;
  font-weight: 400;
  opacity: 0.85;
  margin: 0 0 6px 0;
}
.metric-value{
  font-size: 1.5rem;
  font-weight: 500;
  margin: 0;
  letter-spacing: -0.2px;
}

/* Multi-line text cards */
.wrap p{
  white-space: normal;          /* allow wrapping */
}

/* Optional spacing helper */
.small-gap{
  margin-top: 6px;
}

/* ---------- Color variants (edges + soft glow) ---------- */
.metric {
  background: linear-gradient(135deg, #f8fafc, #eef2ff);
  border-left-color: #4f46e5;
  box-shadow:
    0 6px 20px rgba(79,70,229,0.18),
    inset 0 0 0 1px rgba(79,70,229,0.12);
}

.problem{
  border-left-color: #ef4444;
  box-shadow:
    0 6px 20px rgba(239,68,68,0.18),
    inset 0 0 0 1px rgba(239,68,68,0.12);
}

/* renamed meaning: use same green style for "What this project does" */
.solution{
  border-left-color: #22c55e;
  box-shadow:
    0 6px 20px rgba(34,197,94,0.18),
    inset 0 0 0 1px rgba(34,197,94,0.12);
}

.role-business{
  border-left-color: #f59e0b;
  box-shadow:
    0 6px 20px rgba(245,158,11,0.18),
    inset 0 0 0 1px rgba(245,158,11,0.12);
}
.role-policy{
  border-left-color: #10b981;
  box-shadow:
    0 6px 20px rgba(16,185,129,0.18),
    inset 0 0 0 1px rgba(16,185,129,0.12);
}

/* page cards */
.page{
  border-left-color: #4f46e5;
  box-shadow:
    0 6px 20px rgba(79,70,229,0.18),
    inset 0 0 0 1px rgba(79,70,229,0.12);
}

/* Hover */
.card:hover{
  transform: translateY(-3px);
  transition: all 0.2s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# RENDER
# =========================================================
def render():
    # -------------------------
    # Title
    # -------------------------
    st.markdown('<div class="section-title">Insurance Claim Risk: Context & Objectives</div>', unsafe_allow_html=True)

    # -------------------------
    # Problem -> What this project does (top row, 2 cards)
    # -------------------------
    top1, top2 = st.columns(2)

    problem_text = (
        "Insurance claim data is highly skewed. Most claims are relatively low cost, "
        "while a small number account for disproportionately high charges. Relying on averages "
        "hides this imbalance, making it hard to see where risk concentrates or how to prioritize review."
    )

    project_text = (
        "Provides an end-to-end view of claim risk by combining data quality checks, exploratory analysis, "
        "high-charge flagging, predictive modeling, and an AI FAQ assistant into one workflow."
    )

    with top1:
        st.markdown(f"""
        <div class="card wrap problem">
          <h4>Problem Statement</h4>
          <p>{problem_text}</p>
        </div>
        """, unsafe_allow_html=True)

    with top2:
        st.markdown(f"""
        <div class="card wrap solution">
          <h4>What this project does</h4>
          <p>{project_text}</p>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------
    # Who this is for (vertical, line by line)
    # -------------------------
    st.markdown('<div class="subheader small-gap">Who this is for</div>', unsafe_allow_html=True)

    roles = [
        ("Claims Analysts", "Need to identify and review high-risk claims efficiently.", "solution"),
        ("Business Stakeholders", "Rely on analytics to translate raw claims data into decisions.", "role-business"),
        ("Policy Stakeholders", "Need reliable answers to insurance questions via an AI assistant.", "role-policy"),
    ]

    for title, desc, cls in roles:
        st.markdown(f"""
        <div class="card wrap {cls}">
          <h4>{title}</h4>
          <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# Call render when this page runs
render()