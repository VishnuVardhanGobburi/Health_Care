# Healthcare Insurance Claims Analytics

A production-quality Streamlit application that combines **story-driven Plotly visualizations** for healthcare insurance claims analytics and a **RAG-based FAQ chatbot** for insurance and policy questions, with explicit **accuracy and hallucination testing**.

Built for the Delta Dental Artificial Intelligence Internship, following *Storytelling with Data* principles (Cole Nussbaumer Knaflic).

## Features

- **Context & Big Idea** — Executive intro, KPIs (row count, median/P95 charges, smoker %)
- **Data Quality & Integrity** — Schema validation, missing values, range checks, boxplots and distributions
- **Cost Story** — Sequential narrative: percentiles, smoking, age, BMI, region/sex
- **Anomalies** — Flag high-cost cases (e.g. P95 or IQR); scatter and histogram; sortable table
- **Insurance FAQ Assistant** — RAG chatbot (FAQ/policy only); suggested questions; sources cited
- **Accuracy & Hallucination Testing** — Out-of-scope refusal, source grounding, consistency checks

## Setup

### 1. Clone and install

```bash
cd Health_Care
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Data (fixed paths — no uploads)

Place your datasets at these paths:

| Purpose | Path |
|--------|------|
| Structured claims | `data/medical_insurance.csv` |
| FAQ for RAG | `data/insurance_faq.csv` **or** `data/insurance_docs/` (text files) |

**medical_insurance.csv** should have columns (or close variants):  
`age`, `sex`, `bmi`, `children`, `smoker`, `region`, `charges`

**insurance_faq.csv** should have columns: `question`, `answer` (or similar).

If files are missing, the app will show clear error messages.

### 3. OpenAI API key (chatbot and testing)

Create `.streamlit/secrets.toml` (see `.streamlit/secrets.toml` template) and add:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

Do **not** hardcode, log, or display the API key. The app reads it only via `st.secrets["OPENAI_API_KEY"]`.

### 4. Run

```bash
streamlit run app.py
```

## Project structure

```
Health_Care/
├── app.py                 # Entry point, sidebar navigation
├── pages/
│   ├── one_context.py     # Page 1 — Context & Big Idea
│   ├── two_quality.py     # Page 2 — Data Quality
│   ├── three_cost.py      # Page 3 — Cost Story
│   ├── four_anomaly.py    # Page 4 — Anomalies
│   ├── five_chatbot.py    # Page 5 — FAQ RAG chatbot
│   └── six_testing.py     # Page 6 — Accuracy & hallucination tests
├── src/
│   ├── data.py            # Load, validate, clean (fixed paths)
│   ├── metrics.py         # KPIs, percentiles, summaries
│   ├── viz.py             # Plotly figures (story-driven)
│   ├── anomaly.py         # Anomaly flagging (percentile / IQR)
│   ├── rag.py             # Chunking, embeddings, retrieval
│   └── chat.py            # LLM prompts, guardrails, FAQ-only scope
├── data/
│   ├── medical_insurance.csv
│   └── insurance_faq.csv  (or insurance_docs/)
├── .streamlit/
│   └── secrets.toml       # OPENAI_API_KEY (template only in repo)
├── requirements.txt
└── README.md
```

## Constraints (non-negotiable)

- All visualizations are **Plotly** and interactive; no pie/donut charts.
- **No file uploaders**; all data from predefined local paths.
- Chatbot is **FAQ/policy only** (no analytics or dashboard interpretation).
- **No medical or dental advice.** Anomaly language: “anomaly” or “unusual pattern,” not “fraud.”
- Caching: `st.cache_data` for data/metrics, `st.cache_resource` for vector index.

## License

Use as required by your internship program.
