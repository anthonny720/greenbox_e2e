from django.urls import path

from .views import (ListTreeView, FixedAssetListAPIView, FixedAssetDetailAPIView, PhysicalAssetListAPIView,
                    PhysicalAssetDetailAPIView, ToolListAPIView, ToolDetailAPIView, FailureListAPIView, TypeListAPIView,
                    RequirementsListAPIView, RequirementsDetailAPIView, WorkOrderListView, WorkOrderDetailView,
                    UpdateWorkSupervisorView, UpdateWorkRequesterView, AddResourcesOTView, DeleteResourceOTView,
                    AddHelpersOTView, DeleteHelperOTView, ListTechnicalView, H2OListAPIView, H2ODetailAPIView,
                    ChlorineListAPIView,ChlorineDetailAPIView)

urlpatterns = [path('tree/', ListTreeView.as_view(), name='tree'),
               path('fixed-assets/', FixedAssetListAPIView.as_view(), name='fixed-assets'),
               path('fixed-assets/<str:pk>/', FixedAssetDetailAPIView.as_view(), name='fixed-asset-detail'),
               path('physical-assets/', PhysicalAssetListAPIView.as_view(), name='physical-assets'),
               path('physical-assets/<str:pk>/', PhysicalAssetDetailAPIView.as_view(), name='physical-asset-detail'),
               path('tools/', ToolListAPIView.as_view(), name='tools'),
               path('tools/<str:pk>/', ToolDetailAPIView.as_view(), name='tool-detail'),
               path('failures/', FailureListAPIView.as_view(), name='failures'),
               path('types/', TypeListAPIView.as_view(), name='types'),
               path('requirements/', RequirementsListAPIView.as_view(), name='requirements'),
               path('requirements/<str:pk>/', RequirementsDetailAPIView.as_view(), name='requirements-detail'),
               path('work-orders/', WorkOrderListView.as_view(), name='work-orders'),
               path('work-orders/<str:pk>/update-supervisor/', UpdateWorkSupervisorView.as_view(),
                    name='update-supervisor'),
               path('work-orders/<str:pk>/update-requester/', UpdateWorkRequesterView.as_view(),
                    name='update-requester'),
               path('work-orders/<str:pk>/', WorkOrderDetailView.as_view(), name='work-order-detail'),

               path('work-orders/<str:pk>/add-resources/', AddResourcesOTView.as_view(), name='add-resources'),
                path('work-orders/delete-resources/<str:pk>/', DeleteResourceOTView.as_view(), name='delete-resources'),
                path('work-orders/<str:pk>/add-helpers/', AddHelpersOTView.as_view(), name='add-helpers'),
                path('work-orders/delete-helpers/<str:pk>/', DeleteHelperOTView.as_view(), name='delete-helpers'),
                path('technical/', ListTechnicalView.as_view(), name='technical'),
                path('h2o/', H2OListAPIView.as_view(), name='h2o'),
                path('h2o/<str:pk>/', H2ODetailAPIView.as_view(), name='h2o-detail'),
                path('chlorine/', ChlorineListAPIView.as_view(), name='chlorine'),
                path('chlorine/<str:pk>/', ChlorineDetailAPIView.as_view(), name='chlorine-detail')

               ]
