from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from .views import SearchDNIView, SearchRUCView, SearchDollarView

urlpatterns = [path('auth/', include('djoser.urls')), path('auth/', include('djoser.urls.jwt')),
               path('api/search/dni/<dni>/', SearchDNIView.as_view(), name='search_dni'),
               path('api/search/ruc/<ruc>/', SearchRUCView.as_view(), name='search_ruc'),
               path('api/search/tipo-de-cambio/<date>/', SearchDollarView.as_view(), name='search_date'),
               path('api/users/', include('apps.user.urls'), name='user'),
               path('api/agrisupply/', include('apps.agrisupply.urls'), name='agrisupply'),
               path('api/talent-hub/', include('apps.talent_hub.urls'), name='talent_hub'),
               path('api/commercial/', include('apps.commercial.urls'), name='commercial'),
               path('api/production/', include('apps.production.urls'), name='production'),
               path('api/quality-control/', include('apps.quality_control.urls'), name='quality_control'),
               path('api/maintenance/', include('apps.maintenance.urls'), name='maintenance'),
               path('api/logistic/', include('apps.logistic.urls'), name='logistic'),
               path('api/stakeholders/', include('apps.stakeholders.urls'), name='stakeholders'),
               path('api/category/', include('apps.category.urls'), name='category'),
               path('admin/', admin.site.urls), ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]
