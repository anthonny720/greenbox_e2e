from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (ExternalPeople, Lot, DownloadLot, ItemsLot, Boxes, Pallets, Output, Material, ItemsReceipt,
                     ItemsIssue, Freight, GLP, Files, )


# Register your models here.
@admin.register(ExternalPeople)
class ExternalPeopleAdmin(ImportExportModelAdmin):
    list_display = ('full_name', 'dni', 'phone', 'licence')
    search_fields = ('full_name',)
    ordering = ['full_name']
    list_per_page = 25


@admin.register(Lot)
class LotAdmin(ImportExportModelAdmin):
    list_display = (
    'lot', 'product', 'discount_price_kg', 'discount_price', 'supplier_price', 'supplier', 'manufacturing',
    'datetime_arrival', 'condition', 'stock',)
    search_fields = ('lot',)
    list_editable = ('discount_price_kg', 'discount_price', 'supplier_price',)
    list_filter = ('product', 'supplier', 'manufacturing', 'condition',)
    ordering = ['-datetime_arrival']
    list_per_page = 25


@admin.register(ItemsLot)
class ItemsLotAdmin(ImportExportModelAdmin):
    list_display = ('lot', 'number', 'weight', 'tare',)
    search_fields = ('lot__lot',)
    list_filter = ('lot__product',)
    ordering = ['-lot__datetime_arrival']
    list_per_page = 25


@admin.register(Boxes)
class BoxesAdmin(ImportExportModelAdmin):
    list_display = ('name', 'weight',)
    search_fields = ('name',)
    ordering = ['name']
    list_per_page = 25


@admin.register(Pallets)
class PalletsAdmin(ImportExportModelAdmin):
    list_display = ('name', 'weight',)
    search_fields = ('name',)
    ordering = ['name']
    list_per_page = 25


@admin.register(DownloadLot)
class DownloadLotAdmin(ImportExportModelAdmin):
    list_display = ('lot', 'external', 'cost',)
    search_fields = ('lot__lot', 'external__full_name')
    list_filter = ('lot__product', 'external',)
    ordering = ['-lot__datetime_download_started']
    list_per_page = 25


@admin.register(Freight)
class FreightAdmin(ImportExportModelAdmin):
    list_display = ('lot', 'cost_unit', 'boxes_not_paid', 'cost_false', 'total_cost')
    search_fields = ('lot__lot',)
    list_filter = ('lot__product',)
    ordering = ['-lot__datetime_download_started']
    list_per_page = 25


@admin.register(Output)
class OutputAdmin(ImportExportModelAdmin):
    list_display = ('date', 'lot', 'kg', 'destine',)
    search_fields = ('lot__lot', 'destine',)
    date_hierarchy = 'date'
    ordering = ['-date']
    list_per_page = (25)


@admin.register(GLP)
class GLPAdmin(ImportExportModelAdmin):
    list_display = ('date', 'consumption', 'cost',)
    date_hierarchy = 'date'
    ordering = ['-date']
    list_per_page = 30


@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    list_display = ('name', 'sap', 'group', 'unit_of_measurement',)
    search_fields = ('name', 'name',)
    list_filter = ('group',)
    ordering = ['name']
    list_per_page = 50


@admin.register(ItemsReceipt)
class ItemsReceiptAdmin(ImportExportModelAdmin):
    list_display = (
        'item', 'po_number', 'arrival_date', 'supplier', 'quantity', 'stock', 'price_per_unit', 'manufacturing',)
    search_fields = ('item__name',)
    list_filter = ('item__group',)
    ordering = ['item__name']
    list_per_page = 50


@admin.register(ItemsIssue)
class ItemsIssueAdmin(ImportExportModelAdmin):
    list_display = ('item', 'area', 'date', 'quantity', 'lot_id', 'manufacturing')
    search_fields = ('item__item__name',)
    list_filter = ('item__item__group',)
    ordering = ['item__item__name']
    list_per_page = 50


@admin.register(Files)
class FilesAdmin(ImportExportModelAdmin):
    list_display = ('file', 'lot',)
    search_fields = ('lot__lot',)
    list_filter = ('lot__product',)
    list_per_page = 20
