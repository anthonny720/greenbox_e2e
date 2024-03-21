import uuid

from apps.logistic.models import ItemsProxy
from apps.logistic.models import Material
from django.db import models
from django.utils.text import slugify


# Create your models here.


class SKU(ItemsProxy):
    class Meta:
        verbose_name = 'SKU'
        verbose_name_plural = 'SKUs'
        ordering = ['id']

    performance = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Rendimiento')
    capacity = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name='Capacidad')
    recipe = models.ManyToManyField(Material, verbose_name='Receta', related_name='sku_recipe', through='Recipe')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(SKU, self).save(*args, **kwargs)


class Recipe(models.Model):
    class Meta:
        verbose_name = 'Recetario'
        verbose_name_plural = 'Recetario'

    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    sku = models.ForeignKey(SKU, on_delete=models.PROTECT, verbose_name='SKU', related_name='sku_recipe')

    article = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Articulo',
                                related_name='article_recipe')

    quantity = models.DecimalField(verbose_name='Cantidad', max_digits=12, decimal_places=10, default=0, blank=True)

    def __str__(self):
        return str(self.id)

