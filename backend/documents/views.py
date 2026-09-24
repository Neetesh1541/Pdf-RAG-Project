from django.db.models import Avg, Count, Q
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Conversation, Message
from .models import DocumentUpload
from .serializers import DocumentUploadSerializer
from .services import create_and_process_document, delete_document_assets
from rag.embeddings import delete_document_from_index


class DocumentListUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        documents = DocumentUpload.objects.annotate(num_chunks=Count('chunks')).order_by('-uploaded_at')
        serializer = DocumentUploadSerializer(documents, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'count': documents.count(),
        })

    def post(self, request):
        files = request.FILES.getlist('files') or ([] if 'file' not in request.FILES else [request.FILES['file']])
        if not files:
            return Response({'detail': 'No PDF files supplied.'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors = []
        for uploaded_file in files:
            try:
                document = create_and_process_document(uploaded_file)
                created.append(DocumentUploadSerializer(document, context={'request': request}).data)
            except Exception as exc:
                errors.append({
                    'filename': uploaded_file.name,
                    'error': str(exc),
                })

        response = {'created': created, 'errors': errors}
        code = status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
        return Response(response, status=code)


class DocumentDetailView(APIView):
    def delete(self, request, document_id):
        try:
            document = DocumentUpload.objects.get(id=document_id)
        except DocumentUpload.DoesNotExist:
            return Response({'detail': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)

        delete_document_from_index(document.id)
        delete_document_assets(document)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'detail': 'Query parameter q is required.'}, status=status.HTTP_400_BAD_REQUEST)

        documents = DocumentUpload.objects.filter(
            Q(original_name__icontains=query) | Q(chunks__text__icontains=query)
        ).distinct().prefetch_related('chunks')[:25]

        payload = []
        for document in documents:
            matching_chunks = [chunk for chunk in document.chunks.all() if query.lower() in chunk.text.lower()]
            payload.append({
                'document_id': str(document.id),
                'filename': document.original_name,
                'status': document.status,
                'matches': [
                    {
                        'chunk_id': str(chunk.id),
                        'page_number': chunk.page_number,
                        'snippet': chunk.text[:300],
                    }
                    for chunk in matching_chunks[:5]
                ],
            })
        return Response({'results': payload})


class DashboardView(APIView):
    def get(self, request):
        docs = DocumentUpload.objects.all()
        conversations = Conversation.objects.all().order_by('-updated_at')
        total_questions = Message.objects.filter(role=Message.Role.USER).count()
        average_latency = Message.objects.filter(role=Message.Role.ASSISTANT).aggregate(avg=Avg('latency_ms'))['avg'] or 0

        recent_docs = DocumentUploadSerializer(docs.order_by('-uploaded_at')[:5], many=True, context={'request': request}).data
        recent_conversations = [
            {
                'id': str(c.id),
                'title': c.title,
                'updated_at': c.updated_at,
                'message_count': c.messages.count(),
            }
            for c in conversations[:5]
        ]

        return Response({
            'totals': {
                'documents': docs.count(),
                'pages': sum(d.page_count for d in docs),
                'chunks': sum(d.chunk_count for d in docs),
                'questions': total_questions,
                'average_latency_ms': round(float(average_latency), 2),
            },
            'recent_documents': recent_docs,
            'recent_conversations': recent_conversations,
        })
