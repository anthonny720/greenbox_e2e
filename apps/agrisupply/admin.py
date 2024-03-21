from apps.agrisupply.models import Parcel
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin


# Register your models here.
@admin.register(Parcel)
class ParcelAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('name', 'provider', 'status')
    search_fields = ('name',)
    ordering = ['name']
    list_filter = ('provider',)
    list_per_page = 25
