import time

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import DocumentUpload
from rag.evaluator import evaluate_rag
from rag.graph import run_rag_workflow
from rag.retriever import retrieve_chunks
from .models import Conversation, EvaluationRun, Message
from .serializers import (
    ChatRequestSerializer,
    ConversationSerializer,
    EvaluateRequestSerializer,
    EvaluationRunSerializer,
    MessageSerializer,
)


class ChatView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        message = data['message'].strip()
        document_ids = [str(item) for item in data.get('document_ids', [])]
        if data.get('conversation_id'):
            conversation = get_object_or_404(Conversation, id=data['conversation_id'])
        else:
            conversation = Conversation.objects.create(title=message[:60] or 'New Conversation')

        if document_ids:
            conversation.documents.set(DocumentUpload.objects.filter(id__in=document_ids))

        Message.objects.create(conversation=conversation, role=Message.Role.USER, content=message)

        try:
            start = time.perf_counter()
            result = run_rag_workflow(str(conversation.id), message, document_ids=document_ids)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            assistant = Message.objects.create(
                conversation=conversation,
                role=Message.Role.ASSISTANT,
                content=result['answer'],
                citations=result.get('citations', []),
                latency_ms=latency_ms,
            )
        except Exception as exc:
            return Response(
                {'detail': f'Chat processing failed: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        conversation.title = conversation.title or message[:60]
        conversation.save(update_fields=['title'])

        return Response({
            'conversation': ConversationSerializer(conversation, context={'request': request}).data,
            'assistant_message': MessageSerializer(assistant, context={'request': request}).data,
            'latency_ms': latency_ms,
            'grounded': result.get('grounded', True),
            'confidence': result.get('confidence', 'medium'),
        }, status=status.HTTP_200_OK)


class ConversationListView(APIView):
    def get(self, request):
        conversations = Conversation.objects.prefetch_related('messages').all()
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response({'results': serializer.data, 'count': conversations.count()})


class ConversationDetailView(APIView):
    def get(self, request, conversation_id):
        conversation = get_object_or_404(Conversation.objects.prefetch_related('messages'), id=conversation_id)
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)


class EvaluateView(APIView):
    def post(self, request):
        serializer = EvaluateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get('conversation_id'):
            conversation = get_object_or_404(Conversation, id=data['conversation_id'])
        else:
            conversation = Conversation.objects.create(title='Evaluation Run')

        question = data['question'].strip()
        document_ids = [str(item) for item in data.get('document_ids', [])]
        if document_ids:
            conversation.documents.set(DocumentUpload.objects.filter(id__in=document_ids))

        Message.objects.create(conversation=conversation, role=Message.Role.USER, content=question)

        start = time.perf_counter()
        result = run_rag_workflow(str(conversation.id), question, document_ids=document_ids)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        answer = result['answer']
        chunks = retrieve_chunks(question, document_ids=document_ids)
        metrics = evaluate_rag(question, answer, chunks, data.get('expected_answer', ''))
        metrics['response_latency_ms'] = latency_ms

        run = EvaluationRun.objects.create(
            question=question,
            expected_answer=data.get('expected_answer', ''),
            actual_answer=answer,
            metrics=metrics,
            latency_ms=latency_ms,
        )

        Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=answer,
            citations=result.get('citations', []),
            latency_ms=latency_ms,
        )

        return Response({
            'run': EvaluationRunSerializer(run).data,
            'answer': answer,
            'citations': result.get('citations', []),
            'metrics': metrics,
        }, status=status.HTTP_201_CREATED)
