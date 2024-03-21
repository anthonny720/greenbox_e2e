from apps.stakeholders.models import RawMaterialSupplier
from django.db import models
from simple_history.models import HistoricalRecords

from apps.category.models import Category


# Create your models here.
class Parcel(models.Model):
    class Meta:
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        ordering = ['name']

    status = (('P', 'Presencia'), ('C', 'Limpio'))

    name = models.CharField(max_length=100, verbose_name='Nombre')
    provider = models.ForeignKey(RawMaterialSupplier, on_delete=models.PROTECT, verbose_name='Proveedor', blank=False,
                                 null=False)
    product = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Producto', blank=False, null=False)
    sector = models.CharField(max_length=100, verbose_name='Sector', blank=True, null=True)
    latitude = models.CharField(max_length=100, verbose_name='Latitud', blank=True, null=True)
    longitude = models.CharField(max_length=100, verbose_name='Longitud', blank=True, null=True)
    variety = models.CharField(max_length=100, verbose_name='Variedad', blank=True, null=True)
    fosetil = models.CharField(max_length=100, verbose_name='Fosetil', blank=True, null=True)
    pesticide = models.CharField(max_length=100, verbose_name='Pesticida', blank=True, null=True)

    status = models.CharField(max_length=100, verbose_name='Estado', choices=status, default='P')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
    history = HistoricalRecords()

    def __str__(self):
        return self.name
