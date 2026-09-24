from django.urls import path

from .views import ChatView, ConversationDetailView, ConversationListView, EvaluateView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('evaluate/', EvaluateView.as_view(), name='evaluate'),
]
