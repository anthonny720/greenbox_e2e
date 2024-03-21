import uuid

from django.db import models


# Create your models here.

class PartnerAbstract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Name', blank=True, null=True)
    ruc = models.CharField(max_length=11, unique=True, verbose_name='RUC', blank=False, null=False)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class RawMaterialSupplier(PartnerAbstract):
    class Meta:
        verbose_name = 'Proveedor de Materia Prima'
        verbose_name_plural = 'Proveedores de Materia Prima'


class MaterialSupplier(PartnerAbstract):
    class Meta:
        verbose_name = 'Proveedor de Materiales'
        verbose_name_plural = 'Proveedores de Materiales'


class Client(PartnerAbstract):
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'


class TransportationCompany(PartnerAbstract):
    class Meta:
        verbose_name = 'Empresa de Transporte'
        verbose_name_plural = 'Empresas de Transporte'


class ManufacturingCompany(PartnerAbstract):
    class Meta:
        verbose_name = 'Planta de Producción'
        verbose_name_plural = 'Plantas de Producción'
