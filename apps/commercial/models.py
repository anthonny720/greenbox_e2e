import uuid

from django.db import models
from django_countries.fields import CountryField


class Sample(models.Model):
    class Meta:
        verbose_name = 'Muestra'
        verbose_name_plural = 'Muestras'
        ordering = ['-date']
        db_table  = 'samples_commercial'

    class PackagingType(models.TextChoices):
        ENVELOPE = 'E', 'Sobre'
        BOX = 'B', 'Caja'

    class Status(models.TextChoices):
        ACCEPTED = 'A', 'Solicitud recepcionada y validada'
        DELIVERY_PRODUCTION = 'DP', 'Entrega producción/calidad'
        WAREHOUSE_DELIVERY = 'WD', 'Entrega almacén'
        SENT_TARMA = 'ST', 'Enviado a Tarma'
        RECEIVED_LIMA = 'RL', 'Recibido en Lima'
        SCHEDULE_COURIER = 'SC', 'Programar courier'
        SENT_TO_CLIENT = 'STC', 'Enviado al cliente'
        NOT_DELIVERED = 'ND', 'No entregado'
        RETURN = 'R', 'Devolución'
        CANCELLED = 'C', 'Cancelado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(verbose_name='Fecha de solicitud', auto_now_add=True)
    delivery_date = models.DateField(verbose_name='Fecha de envío (Tarma)')
    applicant = models.CharField(max_length=100, verbose_name='Solicitante', blank=True, null=True)
    code = models.CharField(max_length=100, verbose_name='Código', unique=True)
    client = models.CharField(max_length=100, verbose_name='Cliente')
    delivery_address = models.CharField(max_length=100, verbose_name='Dirección de entrega (Lima)')
    delivery_address_final = models.CharField(max_length=100, verbose_name='Dirección de entrega final')
    country = CountryField(verbose_name='País destino ', blank=True, null=True)
    client_data = models.TextField(verbose_name='Datos de facturación')
    product = models.TextField(verbose_name='Producto')
    specifications = models.TextField(verbose_name='Especificaciones')
    packaging_type = models.CharField(max_length=12, choices=PackagingType.choices, verbose_name='Empaque final',
                                      default=PackagingType.BOX)
    comments = models.TextField(verbose_name='Comentarios', blank=True, null=True)
    status = models.CharField(max_length=19, choices=Status.choices, verbose_name='Estado', default=Status.ACCEPTED)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Peso neto', blank=True, null=True)
    courier = models.CharField(max_length=50, verbose_name='Courier')
    courier_account = models.CharField(max_length=50, verbose_name='Cuenta Courier', blank=True, null=True)
    courier_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Costo courier', default=0)
    shipping_date = models.DateField(verbose_name='Fecha de envío (Cliente)', blank=True, null=True)
    tracking = models.CharField(max_length=100, verbose_name='Tracking', blank=True, null=True)
    estimated_delivery = models.DateField(verbose_name='Fecha estimada de entrega', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def get_packaging_type(self):
        return self.get_packaging_type_display()

    def get_status(self):
        return self.get_status_display()

    def get_country_display(self):
        return self.country
