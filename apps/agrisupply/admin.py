from .models import Parcel, Projection
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from apps.agrisupply.models import Projection


# Register your models here.
@admin.register(Parcel)
class ParcelAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('name', 'provider', 'status')
    search_fields = ('name',)
    ordering = ['name']
    list_filter = ('provider',)
    list_per_page = 25

@admin.register(Projection)
class ProjectionAdmin(ImportExportModelAdmin):
    list_display = ('date', 'product', 'quantity', 'company')
    search_fields = ('date', 'product', 'company')
    ordering = ['date']
    list_filter = ('product', 'company')
    list_per_page = 25