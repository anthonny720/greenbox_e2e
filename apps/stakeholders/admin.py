# Register your models here.
from django.contrib import admin

from .models import RawMaterialSupplier, MaterialSupplier, Client, TransportationCompany, ManufacturingCompany


@admin.register(RawMaterialSupplier)
class RawMaterialSupplierAdmin(admin.ModelAdmin):
    list_display = ("name", 'ruc',)
    search_fields = ("name",)


@admin.register(MaterialSupplier)
class MaterialSupplierAdmin(admin.ModelAdmin):
    list_display = ("name", 'ruc',)
    search_fields = ("name",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", 'ruc',)
    search_fields = ("name",)


@admin.register(TransportationCompany)
class TransportationCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", 'ruc',)
    search_fields = ("name",)


@admin.register(ManufacturingCompany)
class ManufacturingCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", 'ruc',)
    search_fields = ("name",)
