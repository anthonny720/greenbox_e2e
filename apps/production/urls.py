from django.urls import path

from .views import (ConditioningSweetPotatoListView, ConditioningSweetPotatoDetailView, ConditioningPineappleListView,
                    ConditioningPineappleDetailView, ThumbnailProcessListView, ThumbnailDetailView, CutsListView,
                    PackingListView, PackingDetailView)

urlpatterns = [path('conditioning/sweet-potato/', ConditioningSweetPotatoListView.as_view(),
                    name='conditioning-sweet-potato-list'),
               path('conditioning/sweet-potato/<str:pk>/', ConditioningSweetPotatoDetailView.as_view(),
                    name='conditioning-sweet-potato-detail'),
               path('conditioning/pineapple/', ConditioningPineappleListView.as_view(),
                    name='conditioning-pineapple-list'),
               path('conditioning/pineapple/<str:pk>/', ConditioningPineappleDetailView.as_view(),
                    name='conditioning-pineapple-detail'),
               path('packing/', PackingListView.as_view(), name='packing-list'),
               path('packing/<str:pk>/', PackingDetailView.as_view(), name='packing-detail'),
               path('thumbnail/', ThumbnailProcessListView.as_view(), name='thumbnail-process-list'),
               path('thumbnail/<str:pk>/', ThumbnailDetailView.as_view(), name='thumbnail-process-detail'),
               path('cuts/', CutsListView.as_view(), name='cuts-list')

               ]
