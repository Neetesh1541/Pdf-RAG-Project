import os
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone

from .models import DocumentUpload
from rag.ingestion import process_document_file
from rag.embeddings import index_document_chunks, delete_document_from_index

ALLOWED_EXTENSIONS = {'.pdf'}


class DocumentValidationError(Exception):
    pass


def validate_uploaded_pdf(uploaded_file: UploadedFile):
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise DocumentValidationError('Unsupported file type. Please upload a PDF document.')

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if uploaded_file.size > max_bytes:
        raise DocumentValidationError(f'File too large. Max size is {settings.MAX_UPLOAD_SIZE_MB} MB.')

    if uploaded_file.size == 0:
        raise DocumentValidationError('Empty file uploaded.')


def create_and_process_document(uploaded_file: UploadedFile) -> DocumentUpload:
    validate_uploaded_pdf(uploaded_file)

    document = DocumentUpload.objects.create(
        original_name=uploaded_file.name,
        file=uploaded_file,
        file_size=uploaded_file.size,
        status=DocumentUpload.Status.PROCESSING,
        processing_started_at=timezone.now(),
    )

    try:
        extracted_pages = process_document_file(document.file.path)
        chunk_records, extracted_text_length = index_document_chunks(document, extracted_pages)
        document.page_count = len(extracted_pages)
        document.chunk_count = len(chunk_records)
        document.extracted_text_length = extracted_text_length
        document.status = DocumentUpload.Status.READY
        document.completed_at = timezone.now()
        document.error_message = ''
        document.save(update_fields=['page_count', 'chunk_count', 'extracted_text_length', 'status', 'completed_at', 'error_message'])
    except Exception as exc:
        try:
            delete_document_from_index(document.id)
        except Exception:
            pass
        document.chunks.all().delete()
        document.status = DocumentUpload.Status.FAILED
        document.error_message = str(exc)
        document.completed_at = timezone.now()
        document.save(update_fields=['status', 'error_message', 'completed_at'])
        raise

    return document


def delete_document_assets(document: DocumentUpload):
    if document.file and os.path.exists(document.file.path):
        try:
            os.remove(document.file.path)
        except OSError:
            pass
