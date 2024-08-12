from django.urls import path

from .views import (ScannerTrackingView)

urlpatterns = [path('scanner/', ScannerTrackingView.as_view(), name='scanner-tracking'), ]
