import datetime
import decimal
import uuid

from apps.logistic.models import Material
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from simple_history.models import HistoricalRecords

User = get_user_model()


# Create your models here.

class FixedAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Activo Fijo'
        verbose_name_plural = 'Activos Fijos'
        ordering = ['name']


class PhysicalAsset(models.Model):
    class Meta:
        verbose_name = 'Activo Físico'
        verbose_name_plural = 'Activos Físicos'
        ordering = ['name']

    criticality_choices = (('L', 'Baja'), ('M', 'Media'), ('H', 'Alta'),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Nombre')
    buy_date = models.DateField(verbose_name='Fecha de Compra', null=True, blank=True, default=datetime.date.today)
    model = models.CharField(max_length=50, verbose_name='Modelo')
    criticality = models.CharField(max_length=1, verbose_name='Criticidad', choices=criticality_choices, default='L')
    parent = models.ForeignKey(FixedAsset, on_delete=models.PROTECT, related_name='physicals',
                               verbose_name='Activo Fijo')
    code = models.CharField(max_length=50, verbose_name='Código', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Tool(models.Model):
    class Meta:
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'
        ordering = ['name']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Nombre')
    model = models.CharField(max_length=50, verbose_name='Modelo', null=True, blank=True)
    maker = models.CharField(max_length=50, verbose_name='Fabricante', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


# Config
class Failure(models.Model):
    class Meta:
        verbose_name = 'Origen de falla'
        verbose_name_plural = 'Origen de falla'
        ordering = ['name']

    name = models.CharField(max_length=50, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Type(models.Model):
    class Meta:
        verbose_name = 'Tipo de mantenimiento'
        verbose_name_plural = 'Tipo de mantenimiento'
        ordering = ['name']

    name = models.CharField(max_length=50, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Requirements(models.Model):
    class Meta:
        verbose_name = 'Requerimiento'
        verbose_name_plural = 'Requerimientos'
        ordering = ['date']

    class Status(models.TextChoices):
        PENDIENTE = 'Pendiente'
        APROBADO = 'Aprobado'
        RECHAZADO = 'Rechazado'
        PARCIAL = 'Parcial'
        FINALIZADO = 'Finalizado'

    units_choices = (
        ('UN', 'UN'), ('KG', 'KG'), ('LT', 'LT'), ('M2', 'M2'), ('M3', 'M3'), ('M', 'M'), ('CM', 'CM'), ('RL', 'RL'),
        ('CJ', 'CJ'), ('PQ', 'PQ'),)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(verbose_name='Fecha', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario', blank=True, null=True)
    work = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tipo de trabajo')
    item = models.CharField(max_length=100, blank=True, null=True, verbose_name='Item')
    code_item = models.CharField(max_length=100, blank=True, null=True, verbose_name='Código')
    product = models.CharField(max_length=100, blank=True, null=True, verbose_name='Producto')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    quantity = models.IntegerField(blank=True, null=True, verbose_name='Cantidad', default=0)
    unit_measurement = models.CharField(max_length=2, choices=units_choices, default='UN',
                                        verbose_name='Unidad de Medida')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDIENTE, verbose_name='Estado')

    history = HistoricalRecords()

    def __str__(self):
        return self.product

    def save(self, *args, **kwargs):
        if not self.user:
            user = kwargs.pop('user', None)
            if user:
                self.user = user
        super(Requirements, self).save(*args, **kwargs)


class WorkOrder(models.Model):
    date_report = models.DateTimeField(verbose_name='Fecha de reporte', default=timezone.now)
    date_start = models.DateTimeField(verbose_name='Fecha de inicio', blank=True, null=True)
    date_finish = models.DateTimeField(verbose_name='Fecha de finalización', blank=True, null=True)
    asset = models.ForeignKey(PhysicalAsset, on_delete=models.PROTECT, verbose_name='Activo', blank=True, null=True,
                              related_name='work_orders')
    type_maintenance = models.ForeignKey(Type, on_delete=models.PROTECT, verbose_name='Tipo de mantenimiento',
                                         blank=True, null=True)
    failure = models.ForeignKey(Failure, on_delete=models.PROTECT, verbose_name='Origen de falla', blank=True,
                                null=True)
    description = models.TextField(verbose_name='Descripción', blank=True, null=True)
    activities = models.TextField(verbose_name='Actividades', blank=True, null=True)
    technical = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Técnico', blank=True, null=True,
                                  related_name='work_orders_technical')
    helpers = models.ManyToManyField(User, verbose_name='Ayudantes', blank=True, through='HelperItem',
                                     related_name='work_orders_helpers')
    tools = models.ManyToManyField(Tool, verbose_name='Herramientas', blank=True)
    status = models.BooleanField(verbose_name='Estado', default=False)

    planned = models.BooleanField(verbose_name='Planificado', default=False)
    validated = models.BooleanField(verbose_name='Validado', default=False)
    cleaned = models.BooleanField(verbose_name='Limpieza', default=False)
    supervisor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Supervisor', blank=True, null=True,
                                   related_name='work_orders_supervisor')
    requester = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Solicitante', blank=True, null=True,
                                  related_name='work_orders_requester')
    stop = models.BooleanField(verbose_name='Afectó la producción', default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Orden de Trabajo'
        verbose_name_plural = 'Ordenes de Trabajo'
        ordering = ['date_report']

    def __str__(self):
        return self.code

    @property
    def code(self):
        order_number = WorkOrder.objects.filter(date_report__year=self.date_report.year,
                                                created__lt=self.date_report).count() + 1
        return f"OT-{self.date_report.year % 100:02d}{self.date_report.month:02d}{order_number:04d}"

    def get_time(self):
        return self.date_finish - self.date_start if self.date_finish and self.date_start else None

    def get_personnel(self):
        personnel_data = []

        # Procesar el técnico asignado
        if self.technical and self.technical.position:
            technical_duration = self.get_time()
            if technical_duration:
                technical_cost = (technical_duration.total_seconds() / 3600) * float(self.technical.position.salary)
                time_start = self.date_start
                time_end = self.date_finish
                personnel_data.append({'name': self.technical.get_full_name(), 'cost': technical_cost,
                                       'signature': self.technical.get_signature_url(), 'time_start': time_start,
                                       'time_end': time_end})

        for helper in self.helpers_order.select_related('helper__position').all():
            helper_duration = helper.get_time()
            if helper_duration and helper.helper.position:
                helper_cost = (helper_duration.total_seconds() / 3600) * float(helper.helper.position.salary)
                time_start = helper.date_start
                time_end = helper.date_finish
                personnel_data.append({'name': helper.helper.get_full_name(), 'cost': helper_cost,
                                       'signature': helper.helper.get_signature_url(), 'time_start': time_start,
                                       'time_end': time_end})

        return personnel_data


    def get_cost(self):
        return sum(item['cost'] for item in self.get_personnel())

    def get_planner_name(self):
        try:
            user = User.objects.filter(position__name='Planner de mantenimiento').first()
            return user.get_full_name() if user else ""
        except User.DoesNotExist:
            return ""

    def get_signature_by_role(self, position):
        try:
            user = User.objects.filter(position__name=position).first()
            return user.get_signature_url() if user else ""
        except User.DoesNotExist:
            return ""

    def get_signature_planner(self):
        return self.get_signature_by_role('Planner de mantenimiento')

    def get_signature_boss(self):
        return self.get_signature_by_role('Jefe de mantenimiento')

    def get_signature_requester(self):
        try:
            if self.validated:
                user = self.requester
                return user.get_signature_url() if user else ""
            else:
                return ""
        except User.DoesNotExist:
            return ""

    def get_signature_supervisor(self):
        try:
            if self.cleaned:
                user = self.supervisor
                return user.get_signature_url() if user else ""
            else:
                return ""
        except User.DoesNotExist:
            return ""

    def get_resources(self):
        return [
            {'article': item.article, 'quantity': item.quantity, 'id':item.id}
            for item in self.resources_order.all() if self.resources_order is not None
        ]


class HelperItem(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, verbose_name='Orden de trabajo',
                                   related_name='helpers_order')
    helper = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Ayudante', related_name='helpers_helper')
    date_start = models.DateTimeField(verbose_name='Fecha de inicio')
    date_finish = models.DateTimeField(verbose_name='Fecha de finalización')
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Ayudante'
        verbose_name_plural = 'Ayudantes'
        ordering = ['work_order']
        unique_together = ('work_order', 'helper')

    def __str__(self):
        return self.helper.get_full_name() if self.helper else ''

    def get_time(self):
        return self.date_finish - self.date_start if self.date_finish and self.date_start else None


class ResourceItem(models.Model):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, verbose_name='Orden de trabajo',
                                   related_name='resources_order')
    article = models.CharField(max_length=100, verbose_name='Artículo', blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name='Cantidad', default=1)
    class Meta:
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['work_order']

    def __str__(self):
        return self.article if self.article else ''




class H2O(models.Model):
    class Meta:
        verbose_name = 'Consumo de Agua'
        verbose_name_plural = 'Consumo de Agua'
        ordering = ['date']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(verbose_name='Fecha', default=timezone.now, blank=True, null=True)
    m1_day = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M1', blank=True, null=True, default=0)
    m1_night = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M1', blank=True, null=True, default=0)
    m2_day = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M2', blank=True, null=True, default=0)
    m2_night = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M2', blank=True, null=True, default=0)
    m3_day = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M3', blank=True, null=True, default=0)
    m3_night = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M3', blank=True, null=True, default=0)
    m4_day = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M4', blank=True, null=True, default=0)
    m4_night = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M4', blank=True, null=True, default=0)
    m5_day = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M5', blank=True, null=True, default=0)
    m5_night = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M5', blank=True, null=True, default=0)
    m6_day = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M6', blank=True, null=True, default=0)
    m6_night = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='M6', blank=True, null=True, default=0)

    def __str__(self):
        return self.date.strftime('%d/%m/%Y')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.m2_night = self.m2_day if self.m2_day else 0
        super().save(force_insert, force_update, using, update_fields)


class Chlorine(models.Model):
    class Meta:
        verbose_name = 'Control de Cloro'
        verbose_name_plural = 'Control de Cloro'
        ordering = ['date']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(verbose_name='Fecha', default=timezone.now, blank=True, null=True)
    hour = models.TimeField(verbose_name='Hora',  blank=True, null=True)
    dosage_1 = models.IntegerField(verbose_name='Dosificación 1', blank=True, null=True, default=0)
    dosage_2 = models.IntegerField(verbose_name='Dosificación 2', blank=True, null=True, default=0)
    hardness = models.IntegerField(verbose_name='Dureza', blank=True, null=True, default=0)
    ppm = models.PositiveSmallIntegerField(verbose_name='PPM', blank=True, null=True, default=0)
    clean = models.BooleanField(verbose_name='Limpieza', default=False)
    level_1 = models.IntegerField(verbose_name='Nivel 1', blank=True, null=True, default=0)
    level_2 = models.IntegerField(verbose_name='Nivel 2', blank=True, null=True, default=0)
    technical = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Técnico', blank=True, null=True)

    def __str__(self):
        return self.date.strftime('%d/%m/%Y')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.hour = self.hour or timezone.now()
        super().save(force_insert, force_update, using, update_fields)

