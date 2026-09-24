from dataclasses import dataclass
from typing import Iterable

from django.conf import settings

from .embeddings import get_vectorstore


@dataclass
class RetrievedChunk:
    document_id: str
    document_name: str
    page_number: int
    chunk_id: str
    chunk_index: int
    text: str
    distance: float
    relevance: float


def _normalize_score(distance: float) -> float:
    return max(0.0, 1.0 / (1.0 + float(distance)))


def retrieve_chunks(question: str, document_ids: Iterable[str] | None = None, top_k: int | None = None):
    vectorstore = get_vectorstore()
    top_k = top_k or settings.DEFAULT_TOP_K
    candidates = vectorstore.similarity_search_with_score(question, k=top_k * 4)

    results = []
    allowed_ids = {str(item) for item in document_ids} if document_ids else None
    for doc, distance in candidates:
        metadata = doc.metadata or {}
        if allowed_ids and metadata.get('document_id') not in allowed_ids:
            continue
        relevance = _normalize_score(distance)
        results.append(
            RetrievedChunk(
                document_id=str(metadata.get('document_id', '')),
                document_name=str(metadata.get('document_name', 'Unknown document')),
                page_number=int(metadata.get('page_number', 1)),
                chunk_id=str(metadata.get('chunk_id', '')),
                chunk_index=int(metadata.get('chunk_index', 0)),
                text=doc.page_content,
                distance=float(distance),
                relevance=relevance,
            )
        )
        if len(results) >= top_k:
            break

    return results


def format_context(chunks: list[RetrievedChunk]) -> str:
    lines = []
    for index, chunk in enumerate(chunks, start=1):
        lines.append(
            f'[Source {index}] {chunk.document_name} — Page {chunk.page_number}\n{chunk.text}'
        )
    return '\n\n'.join(lines)


def build_citations(chunks: list[RetrievedChunk]):
    citations = []
    seen = set()
    for chunk in chunks:
        key = (chunk.document_id, chunk.page_number)
        if key in seen:
            continue
        seen.add(key)
        citations.append({
            'document_id': chunk.document_id,
            'document_name': chunk.document_name,
            'page_number': chunk.page_number,
            'chunk_id': chunk.chunk_id,
        })
    return citations
