from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Nombre')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True, verbose_name='Padre')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name

