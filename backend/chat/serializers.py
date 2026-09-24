from rest_framework import serializers

from .models import Conversation, EvaluationRun, Message


class MessageSerializer(serializers.ModelSerializer):
    citations = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'citations', 'latency_ms', 'created_at']

    def get_citations(self, obj):
        request = self.context.get('request')
        citations = []
        for citation in obj.citations or []:
            item = dict(citation)
            document_url = item.get('document_url')
            if not document_url and request is not None and item.get('document_id'):
                from documents.models import DocumentUpload

                document = DocumentUpload.objects.filter(id=item['document_id']).first()
                if document and document.file:
                    document_url = request.build_absolute_uri(document.file.url)
                    page_number = item.get('page_number')
                    if page_number:
                        document_url = f'{document_url}#page={page_number}'
            if document_url:
                item['document_url'] = document_url
            citations.append(item)
        return citations


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'message_count', 'messages']

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    conversation_id = serializers.UUIDField(required=False)
    document_ids = serializers.ListField(child=serializers.UUIDField(), required=False)


class EvaluateRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    expected_answer = serializers.CharField(required=False, allow_blank=True)
    conversation_id = serializers.UUIDField(required=False)
    document_ids = serializers.ListField(child=serializers.UUIDField(), required=False)


class EvaluationRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationRun
        fields = ['id', 'question', 'expected_answer', 'actual_answer', 'metrics', 'latency_ms', 'created_at']
