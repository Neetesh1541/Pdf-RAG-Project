import uuid

from django.db import models


class DocumentUpload(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'uploaded', 'Uploaded'
        PROCESSING = 'processing', 'Processing'
        READY = 'ready', 'Ready'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_size = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    page_count = models.PositiveIntegerField(default=0)
    chunk_count = models.PositiveIntegerField(default=0)
    extracted_text_length = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [models.Index(fields=['status', 'uploaded_at'])]

    def __str__(self):
        return self.original_name


class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(DocumentUpload, related_name='chunks', on_delete=models.CASCADE)
    chunk_index = models.PositiveIntegerField()
    page_number = models.PositiveIntegerField(default=1)
    text = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    chroma_id = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document', 'chunk_index']
        unique_together = [('document', 'chunk_index')]
        indexes = [models.Index(fields=['document', 'page_number'])]

    def __str__(self):
        return f'{self.document.original_name} - chunk {self.chunk_index}'
