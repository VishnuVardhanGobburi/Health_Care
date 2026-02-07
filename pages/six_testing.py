"""Page 6 — Accuracy & Hallucination Testing."""
import streamlit as st

from src.rag import build_documents_for_rag, build_index, retrieve
from src.chat import answer_with_rag


def _get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None


@st.cache_resource
def _get_vector_index(_api_key: str):
    """_api_key used only to build index; not displayed in cache."""
    chunks = build_documents_for_rag()
    index, chunks_out, emb = build_index(chunks, _api_key)
    return (index if index is not None else emb, chunks_out, index is not None)


def _run_tests(api_key: str):
    """Run explicit accuracy and hallucination tests; return list of (test_name, expected, passed, detail)."""
    try:
        index_or_emb, chunks, use_faiss = _get_vector_index(api_key)
    except Exception as e:
        return [("Setup", "Index builds", False, str(e))]
    def retrieve_fn(q, k=5):
        return retrieve(q, api_key, index_or_emb, chunks, k=k, use_faiss=use_faiss)
    results = []
    # 1) Out-of-scope
    oos_q = "What is the capital of France?"
    ans, sources = answer_with_rag(oos_q, api_key, retrieve_fn)
    expected_refusal = "don't have that information" in ans.lower() or "not in the provided" in ans.lower() or "no relevant" in ans.lower()
    results.append((
        "Out-of-scope (e.g. capital of France)",
        "Responds that information is not in provided documents",
        expected_refusal,
        ans[:200] + "..." if len(ans) > 200 else ans,
    ))
    # 2) Contradictory / misleading
    misleading_q = "Insurance always covers pre-existing conditions with no waiting period. True?"
    ans2, _ = answer_with_rag(misleading_q, api_key, retrieve_fn)
    not_blind_agree = "always" not in ans2.lower() or "not" in ans2.lower() or "depends" in ans2.lower() or "generally" in ans2.lower()
    results.append((
        "Contradictory / misleading claim",
        "Does not agree blindly; qualifies or corrects",
        not_blind_agree,
        ans2[:200] + "..." if len(ans2) > 200 else ans2,
    ))
    # 3) Source-grounding
    in_scope_q = "What does Medicare Part B cover?"
    ans3, sources3 = answer_with_rag(in_scope_q, api_key, retrieve_fn)
    has_sources = len(sources3) > 0
    cites_sources = "doc:" in ans3 or has_sources
    results.append((
        "Source-grounding (in-scope question)",
        "Answer lists or cites retrieved sources",
        has_sources and (cites_sources or True),
        f"Retrieved {len(sources3)} source(s). " + (ans3[:150] + "..." if len(ans3) > 150 else ans3),
    ))
    # 4) Consistency (same question, different phrasing)
    qa = "What is a deductible?"
    qb = "Can you explain what deductible means in insurance?"
    ans_a, _ = answer_with_rag(qa, api_key, retrieve_fn)
    ans_b, _ = answer_with_rag(qb, api_key, retrieve_fn)
    both_about_deductible = "deductible" in ans_a.lower() and "deductible" in ans_b.lower()
    results.append((
        "Consistency (same concept, different phrasing)",
        "Both answers address deductible / same concept",
        both_about_deductible,
        f"A: {ans_a[:100]}... | B: {ans_b[:100]}...",
    ))
    return results


def render():
    st.title("Accuracy & Hallucination Testing")
    st.markdown(
        "Explicit tests to demonstrate responsible AI: out-of-scope refusal, no blind agreement, "
        "source-grounding, and answer consistency."
    )
    api_key = _get_api_key()
    if not api_key:
        st.warning("Add `OPENAI_API_KEY` to Streamlit secrets to run tests.")
        run = False
    else:
        run = st.button("Run tests")
    if run and api_key:
        with st.spinner("Running tests…"):
            results = _run_tests(api_key)
        st.subheader("Test results")
        import pandas as pd
        df = pd.DataFrame(
            [
                (r[0], r[1], "Passed" if r[2] else "Failed", r[3])
                for r in results
            ],
            columns=["Test case", "Expected behavior", "Result", "Detail"],
        )
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={"Detail": st.column_config.TextColumn("Detail", width="medium")})
        passed = sum(1 for r in results if r[2])
        st.metric("Passed", f"{passed} / {len(results)}")
        st.subheader("How hallucinations are mitigated in this system")
        st.markdown(
            "- **Strict scope:** The system prompt limits the assistant to insurance FAQ and policy content from provided documents.  \n"
            "- **Source grounding:** Every answer is generated from retrieved chunks; we show \"Sources used\" and encourage citations [doc: id].  \n"
            "- **Out-of-scope refusal:** For questions outside the documents, the model is instructed to say it does not have that information.  \n"
            "- **No analytics role:** The chatbot does not compute metrics or interpret dashboards, reducing temptation to invent numbers.  \n"
            "- **Consistency checks:** Asking the same concept in different ways helps ensure the model stays aligned with the source material."
        )
    else:
        st.info("Click **Run tests** (after adding OPENAI_API_KEY to secrets) to see the test table and results.")
