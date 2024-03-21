from django.urls import path

from .views import (AnalysisListView, AnalysisDetailView, )

urlpatterns = [path('analysis/<str:model_name>/', AnalysisListView.as_view(), name='analysis-list'),
    path('analysis/<str:model_name>/<str:pk>/', AnalysisDetailView.as_view(), name='analysis-detail'), ]
