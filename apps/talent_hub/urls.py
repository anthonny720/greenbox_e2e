from django.urls import path

from .views import (StaffListAPIView, StaffDetailAPIView, AbsenteeismListAPIView, TrackingListAPIView,
                    TrackingDetailAPIView, TrackingSummaryListAPIView, CalendarView, SummaryView, OutsourcingView,
                    StaffNotTrackingView, FindUserView, ScannerTrackingView, DepartmentListView)

urlpatterns = [path('staff/', StaffListAPIView.as_view(), name='staff-list'),
               path('staff/<str:pk>/', StaffDetailAPIView.as_view(), name='staff-detail'),
               path('absenteeism/', AbsenteeismListAPIView.as_view(), name='absenteeism-list'),
               path('tracking/', TrackingListAPIView.as_view(), name='tracking-list'),
               path('tracking/<str:pk>/', TrackingDetailAPIView.as_view(), name='tracking-detail'),
               path('tracking-summary/', TrackingSummaryListAPIView.as_view(), name='tracking-summary-list'),
               path('calendar/', CalendarView.as_view(), name='calendar'),
               path('summary/', SummaryView.as_view(), name='summary'),
               path('outsourcing/', OutsourcingView.as_view(), name='outsourcing'),
               path('staff-not-tracking/', StaffNotTrackingView.as_view(), name='staff-not-tracking'),
               path('find-user/', FindUserView.as_view(), name='find-user'),
               path('scanner/', ScannerTrackingView.as_view(), name='scanner-tracking'),
               path('departments/', DepartmentListView.as_view(), name='departments-list')]
