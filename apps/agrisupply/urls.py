from django.urls import path

from .views import ParcelListAPIView, ParcelDetailAPIView

urlpatterns = [
    path('parcel/', ParcelListAPIView.as_view(), name='parcel-list'),
    path('parcel/<int:pk>/', ParcelDetailAPIView.as_view(), name='parcel-detail'),
]