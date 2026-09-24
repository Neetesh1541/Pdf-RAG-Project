from django.urls import path

from .views import DashboardView, DocumentDetailView, DocumentListUploadView, DocumentSearchView

urlpatterns = [
    path('documents/upload/', DocumentListUploadView.as_view(), name='document-upload'),
    path('documents/', DocumentListUploadView.as_view(), name='document-list'),
    path('documents/search/', DocumentSearchView.as_view(), name='document-search'),
    path('documents/<uuid:document_id>/', DocumentDetailView.as_view(), name='document-detail'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
