"""Page 5 — Insurance FAQ Assistant (RAG Chatbot)."""
import streamlit as st

from src.rag import build_documents_for_rag, build_index, retrieve
from src.chat import answer_with_rag


def _get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None


@st.cache_data
def _get_chunks():
    return build_documents_for_rag()


@st.cache_resource
def _get_vector_index(_api_key: str):
    """_api_key prefixed so it is not displayed in cache key; used only to build index."""
    chunks = _get_chunks()
    index, chunks_out, emb = build_index(chunks, _api_key)
    use_faiss = index is not None
    return (index if use_faiss else emb, chunks_out, use_faiss)


def _retrieve_fn(api_key: str, index_or_emb, chunks, use_faiss):
    def fn(query: str, k: int = 5):
        return retrieve(query, api_key, index_or_emb, chunks, k=k, use_faiss=use_faiss)
    return fn


def render():
    st.title("Insurance FAQ Assistant")
    st.markdown(
        "Ask about insurance concepts, policies, and definitions (e.g. copay, deductible, coinsurance). "
        "Answers are grounded in the provided FAQ documents. This assistant does **not** compute metrics or interpret dashboards."
    )
    api_key = _get_api_key()
    if not api_key:
        st.warning("Add `OPENAI_API_KEY` to Streamlit secrets to enable the chatbot. See README and `.streamlit/secrets.toml`.")
        return
    try:
        index_or_emb, chunks, use_faiss = _get_vector_index(api_key)
    except Exception as e:
        st.error(f"Could not build FAQ index. {e}")
        return
    retrieve_fn = _retrieve_fn(api_key, index_or_emb, chunks, use_faiss)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources used"):
                    for s in msg["sources"]:
                        st.caption(f"[doc: {s['id']}] — {s['source']}")
                        st.text(s["text"][:300] + "..." if len(s["text"]) > 300 else s["text"])
    suggested = [
        ("What is a deductible?", "Concepts"),
        ("What does Medicare Part B cover?", "Coverage"),
        ("Is disability insurance required by law?", "Policy"),
        ("What is coinsurance?", "Concepts"),
        ("How is annuity income reported?", "Tax"),
    ]
    st.caption("Suggested questions (by topic):")
    cols = st.columns(min(len(suggested), 5))
    for i, (q, topic) in enumerate(suggested):
        with cols[i % len(cols)]:
            if st.button(f"{topic}: {q[:30]}...", key=f"btn_{i}"):
                st.session_state.messages.append({"role": "user", "content": q})
                answer, sources = answer_with_rag(q, api_key, lambda qq, k=5: retrieve_fn(qq, k))
                st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
                st.rerun()
    prompt = st.chat_input("Ask an insurance or policy question")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        answer, sources = answer_with_rag(prompt, api_key, lambda qq, k=5: retrieve_fn(qq, k))
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
        st.rerun()
