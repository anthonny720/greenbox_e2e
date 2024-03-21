from django.urls import path

from .views import (SamplesAPIView,
SamplesDetailAPIView)

urlpatterns = [
    path('samples/', SamplesAPIView.as_view(), name='samples'),
    path('samples/<str:pk>/', SamplesDetailAPIView.as_view(), name='samples_detail'),
]
