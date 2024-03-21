from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import ConditioningPineapple, ConditioningSweetPotato, ThumbnailProcess, Cuts, PackingLot


@admin.register(ConditioningPineapple)
class ConditioningPineappleAdmin(ImportExportModelAdmin):
    list_display = (
        'date', 'lot', 'logistic_kg', 'rejected_kg', 'process_kg', 'enabled_kg', 'crown_kg', 'shell_trunk_kg',
        'pulp_juice_kg', 'brix', 'ph', 'people', 'duration', 'number_changes')
    list_filter = ('date', 'lot', 'brix', 'ph')
    date_hierarchy = 'date'
    search_fields = ('lot__lot',)
    ordering = ['-date']
    list_per_page = (20)

@admin.register(Cuts)
class CutsAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ['name']
    list_per_page = 20


@admin.register(ConditioningSweetPotato)
class ConditioningSweetPotatoAdmin(ImportExportModelAdmin):
    list_display = (
        'date', 'lot', 'logistic_kg', 'rejected_kg', 'process_kg', 'enabled_kg', 'waste_kg', 'brix', 'ph', 'people',
        'duration', 'number_changes')
    list_filter = ('date', 'lot', 'brix', 'ph')
    date_hierarchy = 'date'
    search_fields = ('lot__lot',)
    ordering = ['-date']
    list_per_page = 20


@admin.register(ThumbnailProcess)
class ThumbnailProcessAdmin(ImportExportModelAdmin):
    list_display = ('photo', 'lot',)
    search_fields = ('lot__lot',)
    list_filter = ('lot__product',)
    list_per_page = 20

@admin.register(PackingLot)
class PackingLotProcessAdmin(ImportExportModelAdmin):
    list_display = ('date_production','date_packaging', 'lot', 'cut', 'kg',)
    date_hierarchy = 'date_packaging'
    search_fields = ('lot__lot',)
    ordering = ['-date_packaging']
    list_per_page = 20
