from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import AnalysisPineapple, AnalysisSweetPotato


@admin.register(AnalysisPineapple)
class AnalysisPineappleAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('lot',)
    list_filter = ['lot__lot']
    date_hierarchy = 'lot__datetime_download_started'
    list_per_page = 50


@admin.register(AnalysisSweetPotato)
class AnalysisSweetPotatoAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('lot',)
    list_filter = ['lot__lot']
    date_hierarchy = 'lot__datetime_download_started'
    list_per_page = 50
