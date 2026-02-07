"""
LLM calls, prompts, and guardrails for the FAQ chatbot.
Chatbot is FAQ/policy only; does not compute metrics or interpret dashboards.
"""
from __future__ import annotations

from typing import Any

# System prompt: scope and guardrails
SYSTEM_PROMPT = """You are an insurance FAQ assistant. Your role is to answer questions about insurance concepts, policies, and common definitions (e.g., copay, deductible, coinsurance) using ONLY the provided source documents.

Rules:
- Base every answer on the retrieved context. If the context does not contain enough information, say: "I don't have that information in the provided documents."
- Do NOT compute metrics, interpret dashboards, or analyze data. Only explain insurance concepts and policy-related questions.
- Do NOT give medical or dental advice.
- When you use information from the context, cite the source as [doc: <source_id>].
- If no relevant sources were retrieved, say so and do not invent an answer.
- Keep answers concise and professional."""


def build_messages(
    context_chunks: list[tuple[dict, float]],
    user_query: str,
) -> list[dict[str, str]]:
    """Build context string and message list for OpenAI."""
    context_parts = []
    for chunk, _ in context_chunks:
        doc_id = chunk.get("doc_id", chunk.get("id", "unknown"))
        context_parts.append(f"[doc: {doc_id}]\n{chunk.get('text', '')}")
    context = "\n\n---\n\n".join(context_parts) if context_parts else ""
    if not context:
        context = "(No relevant documents retrieved.)"
    return [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\nRetrieved context:\n" + context},
        {"role": "user", "content": user_query},
    ]


def call_llm(
    messages: list[dict[str, str]],
    api_key: str,
    model: str = "gpt-4o-mini",
) -> str:
    """Call OpenAI chat and return assistant content."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError("OpenAI package required for chatbot.") from e
    client = OpenAI(api_key=api_key)
    r = client.chat.completions.create(model=model, messages=messages)
    return r.choices[0].message.content or ""


def answer_with_rag(
    query: str,
    api_key: str,
    retrieve_fn: Any,
    top_k: int = 5,
) -> tuple[str, list[dict]]:
    """
    Retrieve chunks, build messages, call LLM. Returns (answer_text, list of source chunks).
    """
    results = retrieve_fn(query, k=top_k)
    chunks_with_dist = [(c, d) for c, d in results]
    sources = [{"id": c.get("doc_id", c.get("id")), "text": c.get("text", "")[:200], "source": c.get("source", "")} for c, _ in chunks_with_dist]
    messages = build_messages(chunks_with_dist, query)
    answer = call_llm(messages, api_key=api_key)
    return answer, sources
