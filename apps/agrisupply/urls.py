from django.urls import path

from .views import ParcelListAPIView, ParcelDetailAPIView, ProjectionListAPIView, ProjectionDetailAPIView

urlpatterns = [
    path('parcel/', ParcelListAPIView.as_view(), name='parcel-list'),
    path('parcel/<int:pk>/', ParcelDetailAPIView.as_view(), name='parcel-detail'),
    path('projection/', ProjectionListAPIView.as_view(), name='projection-list'),
    path('projection/<int:pk>/', ProjectionDetailAPIView.as_view(), name='projection-detail'),
]
