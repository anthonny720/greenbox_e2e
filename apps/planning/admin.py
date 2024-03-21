from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from apps.planning.models import SKU, Recipe


# Register your models here.
@admin.register(SKU)
class SKUAdmin(ImportExportModelAdmin):
    list_display = ('name', 'sap', 'group', 'performance', 'capacity')
    search_fields = ('name', 'group')
    ordering = ['name']
    list_per_page = (25)


@admin.register(Recipe)
class RecipeAdmin(ImportExportModelAdmin):
    list_display = ('sku', 'article', 'quantity')
    search_fields = ('sku__name', 'article__name')
    list_filter = ('sku', 'article')
    ordering = ['sku__name']
    list_per_page = (25)
