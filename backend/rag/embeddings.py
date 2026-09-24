from functools import lru_cache
from typing import Iterable
from uuid import UUID

from django.conf import settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document as LCDocument
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from documents.models import DocumentChunk, DocumentUpload

COLLECTION_NAME = 'researchmind_documents'


@lru_cache(maxsize=1)
def get_embeddings():
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError('GOOGLE_API_KEY is not configured.')
    return GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )


@lru_cache(maxsize=1)
def get_chat_model():
    if not settings.GOOGLE_API_KEY:
        raise RuntimeError('GOOGLE_API_KEY is not configured.')
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_CHAT_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
    )


@lru_cache(maxsize=1)
def get_vectorstore():
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(settings.CHROMA_PERSIST_DIR),
    )


def _split_page_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1100,
        chunk_overlap=180,
        separators=['\n\n', '\n', '. ', ' ', ''],
    )
    return splitter.split_text(text)


def index_document_chunks(document: DocumentUpload, extracted_pages: Iterable[dict]):
    vectorstore = get_vectorstore()
    chunk_records = []
    chunk_documents = []
    chunk_ids = []
    total_chars = 0
    chunk_index = 0

    for page in extracted_pages:
        page_text = page.get('text', '')
        total_chars += len(page_text)
        for chunk_text in _split_page_text(page_text):
            chunk_index += 1
            chunk = DocumentChunk(
                document=document,
                chunk_index=chunk_index,
                page_number=page['page_number'],
                text=chunk_text,
                metadata={
                    'document_id': str(document.id),
                    'filename': document.original_name,
                    'page_number': page['page_number'],
                    'chunk_index': chunk_index,
                },
            )
            chunk_records.append(chunk)
            chunk_ids.append(str(chunk.id))
            chunk_documents.append(
                LCDocument(
                    page_content=chunk_text,
                    metadata={
                        'document_id': str(document.id),
                        'document_name': document.original_name,
                        'page_number': page['page_number'],
                        'chunk_index': chunk_index,
                        'chunk_id': str(chunk.id),
                    },
                )
            )

    DocumentChunk.objects.bulk_create(chunk_records)
    if chunk_documents:
        vectorstore.add_documents(chunk_documents, ids=chunk_ids)

    for chunk_obj, chroma_id in zip(chunk_records, chunk_ids):
        chunk_obj.chroma_id = chroma_id
    DocumentChunk.objects.bulk_update(chunk_records, ['chroma_id'])

    return chunk_records, total_chars


def delete_document_from_index(document_id: UUID | str):
    vectorstore = get_vectorstore()
    document_id = str(document_id)
    try:
        vectorstore._collection.delete(where={'document_id': document_id})
    except Exception:
        # Best-effort deletion; the document can still be removed from the database.
        pass
