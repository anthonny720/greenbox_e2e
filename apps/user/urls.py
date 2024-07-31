from django.urls import path

from .views import (DepartmentsListAPIView, PositionListAPIView)

urlpatterns = [path('departments/', DepartmentsListAPIView.as_view(), name='departments-list'),
               path('positions/', PositionListAPIView.as_view(), name='positions-list'),

               ]
