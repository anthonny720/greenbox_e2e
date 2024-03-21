# Register your models here.
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import FixedAsset, PhysicalAsset, Tool, Requirements, Failure, Type, WorkOrder, ResourceItem, Chlorine, H2O


# Register your models here.
@admin.register(FixedAsset)
class FixedAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ['name']
    list_per_page = 25


@admin.register(PhysicalAsset)
class PhysicalAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('name', 'criticality', 'parent',)
    list_filter = ('criticality', 'parent',)
    search_fields = ('name',)
    ordering = ['name']
    list_per_page = 25


@admin.register(Tool)
class ToolAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ['name']
    list_per_page = 25


# Register your models here.
@admin.register(Failure)
class FailureAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    ordering = ['-name']
    list_per_page = 25


@admin.register(Type)
class TypeAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    ordering = ['-name']
    list_per_page = 25


@admin.register(Requirements)
class RequirementsAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('date', 'user', 'product', 'quantity', 'unit_measurement', 'status')
    list_filter = ('user', 'date',)
    search_fields = ('product', 'description',)
    ordering = ['date']
    list_per_page = 25


@admin.register(WorkOrder)
class WorkOrderAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('code', 'date_report', 'date_start', 'type_maintenance', 'failure', 'status')
    list_filter = ('technical', 'status', 'type_maintenance', 'failure')
    date_hierarchy = 'date_start'
    search_fields = ('description', 'observations',)
    ordering = ['-date_report']
    list_per_page = 25


@admin.register(ResourceItem)
class ResourceItemAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('work_order', 'article', 'quantity')
    ordering = ['-work_order']
    list_per_page = 25


@admin.register(Chlorine)
class ChlorineItemAdmin(ImportExportModelAdmin):
    list_display = ('date', 'hour', 'technical')
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 30


@admin.register(H2O)
class H2OItemAdmin(ImportExportModelAdmin):
    list_display = ('date',)
    ordering = ['-date']
    date_hierarchy = 'date'
    list_per_page = 30
