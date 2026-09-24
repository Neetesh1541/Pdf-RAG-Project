import math
import re
from collections import Counter
from typing import Iterable

from .retriever import RetrievedChunk


def _tokens(text: str):
    return re.findall(r'[a-z0-9]+', text.lower())


def _jaccard(a: str, b: str) -> float:
    set_a, set_b = set(_tokens(a)), set(_tokens(b))
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _overlap_ratio(source: str, target: str) -> float:
    source_tokens = Counter(_tokens(source))
    target_tokens = Counter(_tokens(target))
    if not source_tokens or not target_tokens:
        return 0.0
    overlap = sum(min(source_tokens[t], target_tokens[t]) for t in source_tokens.keys() & target_tokens.keys())
    return overlap / max(1, sum(target_tokens.values()))


def evaluate_rag(question: str, answer: str, retrieved_chunks: Iterable[RetrievedChunk], expected_answer: str = '') -> dict:
    chunks = list(retrieved_chunks)
    context_text = ' '.join(chunk.text for chunk in chunks)
    retrieval_relevance = round(sum(chunk.relevance for chunk in chunks) / max(1, len(chunks)), 4)
    context_relevance = round(max((chunk.relevance for chunk in chunks), default=0.0), 4)
    answer_relevance = round(_jaccard(question, answer), 4)
    faithfulness = round(_overlap_ratio(context_text, answer), 4)
    expected_alignment = round(_jaccard(expected_answer, answer), 4) if expected_answer else 0.0

    return {
        'retrieval_relevance': retrieval_relevance,
        'context_relevance': context_relevance,
        'answer_relevance': answer_relevance,
        'faithfulness': faithfulness,
        'expected_alignment': expected_alignment,
    }
