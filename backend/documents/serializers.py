from rest_framework import serializers

from .models import DocumentChunk, DocumentUpload


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'chunk_index', 'page_number', 'text', 'metadata', 'chroma_id']


class DocumentUploadSerializer(serializers.ModelSerializer):
    chunks = DocumentChunkSerializer(many=True, read_only=True)
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentUpload
        fields = [
            'id',
            'original_name',
            'document_url',
            'file_size',
            'uploaded_at',
            'status',
            'page_count',
            'chunk_count',
            'extracted_text_length',
            'error_message',
            'processing_started_at',
            'completed_at',
            'chunks',
        ]
        read_only_fields = fields

    def get_document_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get('request')
        url = obj.file.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
