from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Tracking, Holiday, Staff, Absenteeism
from .resources import StaffResource


# Register your models here.

@admin.register(Tracking)
class TrackingAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('staff', 'date', 'worked_hours', 'check_in', 'lunch_start', 'lunch_end', 'check_out', 'absenteeism',
                    'absenteeism_hours',)
    search_fields = ('staff__full_name',)
    list_filter = ('staff__area__name', 'staff__trusted', 'staff__hours_per_day',)
    date_hierarchy = 'date'
    list_per_page = 25


@admin.register(Holiday)
class HolidayAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('name', 'date',)


@admin.register(Staff)
class StaffAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = StaffResource
    list_display = ('name', 'last_name', 'dni', 'area', 'status',)
    search_fields = ('name', 'last_name', 'dni',)
    ordering = ['name']
    list_filter = ('area', 'status', 'trusted', 'hours_per_day', 'hours_saturday', 'hours_sunday',)
    list_editable = ('status',)
    list_per_page = 25


@admin.register(Absenteeism)
class AbsenteeismAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ['name']
    list_filter = ('name',)
    list_per_page = 25
