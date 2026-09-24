import json
import re
from typing import Any

from django.conf import settings

from .embeddings import get_chat_model
from .retriever import RetrievedChunk, build_citations, format_context

FALLBACK_TEXT = "I couldn't find sufficient evidence in the uploaded documents."


def _strip_json(text: str) -> str:
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    return text


def _parse_model_output(raw_text: str) -> dict[str, Any]:
    cleaned = _strip_json(raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            'answer': cleaned,
            'citations': [],
            'confidence': 'low',
        }


def _format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return 'No prior conversation.'
    lines = []
    for message in history[-8:]:
        lines.append(f"{message['role'].title()}: {message['content']}")
    return '\n'.join(lines)


def generate_grounded_answer(question: str, history: list[dict[str, str]], chunks: list[RetrievedChunk]):
    if not chunks:
        return {
            'answer': FALLBACK_TEXT,
            'citations': [],
            'confidence': 'low',
            'grounded': False,
        }

    top_relevance = max(chunk.relevance for chunk in chunks)
    if top_relevance < settings.RAG_MIN_SCORE:
        return {
            'answer': FALLBACK_TEXT,
            'citations': build_citations(chunks),
            'confidence': 'low',
            'grounded': False,
        }

    context = format_context(chunks)
    prompt = f"""
You are ResearchMind AI, a careful research assistant.
Answer the user's question using only the provided document context and conversation history.

Rules:
- Do not invent facts.
- If the answer is not supported by the context, say exactly: {FALLBACK_TEXT}
- Prefer concise, evidence-based, research-style language.
- Return valid JSON with keys: answer, citations, confidence.
- citations must be a list of objects with document_name and page_number.
- If multiple documents support the answer, cite them all.

Conversation history:
{_format_history(history)}

Retrieved context:
{context}

Question:
{question}
"""

    model = get_chat_model()
    response = model.invoke(prompt)
    content = getattr(response, 'content', str(response))
    parsed = _parse_model_output(content)

    answer = parsed.get('answer') or FALLBACK_TEXT
    citations = build_citations(chunks)
    confidence = parsed.get('confidence', 'medium')

    return {
        'answer': answer,
        'citations': citations,
        'confidence': confidence,
        'grounded': answer != FALLBACK_TEXT,
        'raw': content,
    }
