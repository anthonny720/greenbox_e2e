import decimal
import uuid

from apps.agrisupply.models import Parcel
from apps.category.models import Category
from apps.stakeholders.models import MaterialSupplier
from apps.stakeholders.models import (RawMaterialSupplier, TransportationCompany, ManufacturingCompany, )
from apps.user.models import Departments
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords


# Create your models here.
class Boxes(models.Model):
    class Meta:
        verbose_name = 'Jabas'
        verbose_name_plural = 'Jabas'

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100, verbose_name='Nombre', blank=False, null=False, unique=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Peso', blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Pallets(models.Model):
    class Meta:
        verbose_name = 'Pallets'
        verbose_name_plural = 'Pallets'

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100, verbose_name='Nombre', blank=False, null=False, unique=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Peso', blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ExternalPeople(models.Model):
    class Meta:
        verbose_name = 'Persona Externa'
        verbose_name_plural = 'Personas Externas'

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    full_name = models.CharField(max_length=100, verbose_name='Nombre Completo', blank=True, null=True)
    dni = models.CharField(max_length=8, verbose_name='DNI', blank=False, null=False, unique=True)
    phone = models.CharField(max_length=9, verbose_name='Teléfono', blank=True, null=True)
    licence = models.CharField(max_length=100, verbose_name='Licencia', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Lot(models.Model):
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['datetime_download_started']

    condition_choices = (('O', 'Organico'), ('C', 'Convencional'),)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    lot = models.CharField(max_length=13, verbose_name='Lote', blank=False, null=False, unique=True)
    product = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Producto', blank=False, null=False)
    supplier = models.ForeignKey(RawMaterialSupplier, on_delete=models.PROTECT, verbose_name='Proveedor', blank=False,
                                 null=False)
    transport = models.ForeignKey(TransportationCompany, on_delete=models.PROTECT, verbose_name='Transporte',
                                  blank=True, null=True)
    manufacturing = models.ForeignKey(ManufacturingCompany, on_delete=models.PROTECT, verbose_name='Planta de proceso',
                                      blank=False, null=False)
    origin = models.CharField(max_length=100, verbose_name='Origen', blank=True, null=True)
    parcels = models.ManyToManyField(Parcel, verbose_name='Parcelas', blank=True)
    parcels_string = models.CharField(max_length=200, verbose_name='Parcelas', blank=True, null=True, default='')
    transport_guide = models.CharField(max_length=30, verbose_name='Guía de Transporte', blank=True, null=True)
    supplier_guide = models.CharField(max_length=30, verbose_name='Guía de Proveedor', blank=True, null=True)
    invoice = models.CharField(max_length=30, verbose_name='Factura', blank=True, null=True)
    datetime_arrival = models.DateTimeField(verbose_name='Fecha de Llegada', blank=False, null=False)
    datetime_departure = models.DateTimeField(verbose_name='Fecha de Salida', blank=True, null=True)
    datetime_download_started = models.DateTimeField(verbose_name='Fecha de Inicio de Descarga', blank=False,
                                                     null=False)
    datetime_download_finished = models.DateTimeField(verbose_name='Fecha de Fin de Descarga', blank=True, null=True)
    condition = models.CharField(max_length=1, choices=condition_choices, verbose_name='Condición', blank=False,
                                 null=False)
    variety = models.CharField(max_length=25, verbose_name='Variedad', blank=True, null=True)
    guide_weight = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Peso de Guía', blank=True,
                                       null=True, default=0)
    sample_weight = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Peso de Muestra', blank=True,
                                        null=True, default=0)
    observation = models.TextField(verbose_name='Observación', blank=True, null=True)
    discount_description = models.TextField(verbose_name='Descripción de Descuento', blank=True, null=True)
    discount_price_kg = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Kg de Descuento precio',
                                            blank=True, null=True, default=0)
    discount_price = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Precio de Descuento', blank=True,
                                         default=0, null=True)

    stock = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Stock', blank=True, null=True, default=0)
    supplier_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Precio de Proveedor/Campo',
                                         blank=True, null=True)
    block = models.BooleanField(verbose_name='Bloqueado', blank=True, null=True, default=False)
    freight_boxes = models.IntegerField(verbose_name='Flete por envio de jabas', blank=True, null=True, default=0)

    # Other fields to be added but edition is blocked for calculation purposes
    discount_weight_percentage = models.DecimalField(max_digits=12, decimal_places=8, default=0,
                                                     verbose_name='Porcentaje de Peso de Descuento', blank=True,
                                                     null=True, editable=False)
    boxes = models.IntegerField(verbose_name='Contenedores', blank=True, null=True, editable=False, default=0)
    pallets = models.IntegerField(verbose_name='Pallets', blank=True, null=True, editable=False, default=0)
    weight_net = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Peso Neto', blank=True, null=True,
                                     editable=False, default=0)
    weight_gross = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Peso Bruto', blank=True, null=True,
                                       editable=False, default=0)
    weight_usable = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Peso Utilizable', blank=True,
                                        null=True, editable=False, default=0)
    weight_reject = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Peso de Rechazo', blank=True,
                                        null=True, editable=False, default=0)
    weight_boxes = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Tara', blank=True, null=True,
                                       editable=False, default=0)
    weight_pallet = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Peso de Pallet', blank=True,
                                        null=True, editable=False, default=0)
    download_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Precio de Descarga', blank=True,
                                         null=True, editable=False, default=0)
    freight = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Flete', blank=True, null=True,
                                  default=0, editable=False)
    plant_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Precio de Planta', blank=True,
                                      null=True, editable=False, default=0)
    total_amount = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Monto Total', blank=True,
                                       null=True, editable=False, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.lot

    def calc_weight_reject(self):
        total_rejected_kg_pineapple = self.conditioningpineapple_set.aggregate(total=Sum('rejected_kg'))['total'] or 0
        total_rejected_kg_sweetpotato = self.conditioningsweetpotato_set.aggregate(total=Sum('rejected_kg'))['total'] or 0
        total_rejected_kg = total_rejected_kg_pineapple + total_rejected_kg_sweetpotato
        self.weight_reject = total_rejected_kg
        self.discount_weight_percentage = round(total_rejected_kg / self.weight_net * 100,
                                                8) if self.weight_net > 0 else 0
        self.weight_usable = self.weight_net - total_rejected_kg if self.weight_net > 0 else 0
        self.save(update_fields=['weight_reject', 'discount_weight_percentage', 'weight_usable'])


    def save(self, *args, **kwargs):
        self.parcels_string = ', '.join([parcel.name for parcel in self.parcels.all()]) if self.parcels.all() else ''
        self.stock = self.calc_stock()
        self.total_amount = self.calc_total_amount()
        self.plant_price = self.total_amount / self.weight_usable if self.weight_usable > 0 else 0
        super(Lot, self).save(*args, **kwargs)

    def calc_total_amount(self):
        supplier_price = self.supplier_price or 0
        first_kg = self.weight_usable - self.discount_price_kg if self.weight_usable > 0 else 0
        discount_price = self.discount_price_kg * self.discount_price if self.discount_price_kg > 0 else 0

        freight = self.freight or 0
        download_price = self.download_price or 0
        freight_boxes = self.freight_boxes or 0

        total_amount = supplier_price * first_kg + freight + download_price + freight_boxes + discount_price
        return total_amount

    def calc_stock(self):
        weight_net = decimal.Decimal(self.weight_net) - decimal.Decimal(self.sample_weight) if self.weight_net > 0 else 0
        output = self.output.aggregate(total=Sum('kg'))['total'] or 0
        stock = decimal.Decimal(weight_net) - decimal.Decimal(output) if weight_net > 0 else 0
        return stock

    def calc_items_fields(self):
        try:
            items_lot = self.items_lot.all().select_related('pallet')
            self.boxes = self.pallets = self.weight_boxes = self.weight_pallet = self.stock = 0
            for item in items_lot:
                self.boxes += item.box_0_25 + item.box_0_5 + item.box_1 + item.box_1_5 + item.box_1_6
                self.pallets += 1
                self.weight_boxes += item.get_weight_boxes()
                self.weight_pallet += item.pallet.weight
            self.weight_net = items_lot.aggregate(total=Sum('weight'))['total'] or 0
            self.weight_net += self.sample_weight
            self.weight_net -= items_lot.aggregate(total=Sum('tare'))['total'] or 0
            self.weight_gross = self.weight_boxes + self.weight_net
            self.save(update_fields=['boxes', 'pallets', 'weight_boxes', 'weight_pallet', 'weight_net', 'weight_gross'])
        except ObjectDoesNotExist as e:
            pass


@receiver(post_save, sender=Lot)
def add_freight(sender, instance, created, **kwargs):
    if created:
        Freight.objects.create(lot=instance, cost_unit=0, boxes_not_paid=0, cost_false=0, total_cost=0)
        DownloadLot.objects.create(lot=instance, cost=0, status='P')


def get_file_path(instance, filename):
    file = f'lot/{instance.lot.lot}/{filename}'
    return file


class Files(models.Model):
    class Meta:
        verbose_name = 'Archivo'
        verbose_name_plural = 'Archivos'

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    file = models.FileField(upload_to=get_file_path, verbose_name='Archivo', blank=False, null=False)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, verbose_name='Lote', blank=True, null=True,
                            related_name='files_lot')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name


@receiver(post_delete, sender=Files)
def post_delete_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)


class ItemsLot(models.Model):
    class Meta:
        verbose_name = 'Item de Lote'
        verbose_name_plural = 'Items de Lotes'
        unique_together = ('lot', 'number')
        ordering = ['number']

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='items_lot')
    number = models.IntegerField(verbose_name='Número', blank=False, null=False)
    weight = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Peso', blank=False, null=False,
                                 default=0)
    box_0 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Jabas 0 kg', blank=False, null=False,
                                default=0)
    box_0_25 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Jabas 0.25 kg', blank=False,
                                   null=False, default=0)
    box_0_5 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Jabas 0.5 kg', blank=False, null=False,
                                  default=0)
    box_1 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Jabas 1 kg', blank=False, null=False,
                                default=0)
    box_1_5 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Jabas 1.5 kg', blank=False, null=False,
                                  default=0)
    box_1_6 = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Jabas 1.6 kg', blank=False, null=False,
                                  default=0)
    pallet = models.ForeignKey(Pallets, on_delete=models.PROTECT, verbose_name='Pallet', blank=False, null=False)
    tare = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Tara', blank=True, null=True, default=0)
    c6 = models.IntegerField(default=0, verbose_name="Calibre 6")
    c8 = models.IntegerField(default=0, verbose_name="Calibre 8")
    c10 = models.IntegerField(default=0, verbose_name="Calibre 10")
    c12 = models.IntegerField(default=0, verbose_name="Calibre 12")
    c14 = models.IntegerField(default=0, verbose_name="Calibre 14")
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.lot.lot} - {self.number}'

    def save(self, *args, **kwargs):
        self.tare = self.get_tare()
        super(ItemsLot, self).save(*args, **kwargs)

    BOXES_MAPPING = {'SN': 'box_0', 'Jaba 0.25': 'box_0_25', 'Jaba 0.5': 'box_0_5', 'Jaba 1.0': 'box_1',
                     'Jaba 1.5': 'box_1_5', 'Jaba 1.6': 'box_1_6', }

    def get_weight_boxes(self):
        total_weight = 0
        try:
            for box_name, attr_name in self.BOXES_MAPPING.items():
                box_quantity = getattr(self, attr_name)
                box_weight = Boxes.objects.filter(name=box_name).first()
                total_weight += box_quantity * box_weight.weight
            return total_weight
        except ObjectDoesNotExist as e:
            return str(e)

    def get_tare(self):
        try:
            return self.get_weight_boxes() + self.pallet.weight
        except ObjectDoesNotExist:
            return 0

    def get_net_weight(self):
        try:
            return self.weight - self.get_tare()
        except ObjectDoesNotExist:
            return 0


@receiver(post_save, sender=ItemsLot)
@receiver(post_delete, sender=ItemsLot)
def dispatch_after_delete_update(sender, instance, **kwargs):
    instance.lot.calc_items_fields()


class DownloadLot(models.Model):
    class Meta:
        verbose_name = 'Servicio estiba/descarga'
        verbose_name_plural = 'Servicios estiba/descarga'
        ordering = ['-lot__datetime_download_started']

    status_choices = (('P', 'Pendiente'), ('F', 'Finalizado'),)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    lot = models.OneToOneField(Lot, on_delete=models.PROTECT, verbose_name='Lote', blank=False, null=False,
                               related_name='download_lot')
    payment_date = models.DateTimeField(verbose_name='Fecha de Pago', blank=True, null=True)
    status = models.CharField(max_length=1, choices=status_choices, verbose_name='Estado', blank=False, null=False,
                              default='P')
    cost = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Costo', blank=True, null=True)
    external = models.ForeignKey(ExternalPeople, on_delete=models.PROTECT, verbose_name='Persona Externa', blank=True,
                                 null=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.lot.lot} - {self.status} - {self.payment_date} - {self.cost} - {self.external}'

    def save(self, *args, **kwargs):
        self.lot.download_price = self.cost
        self.lot.save()
        super(DownloadLot, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.lot.download_price = 0
        self.lot.save()
        super(DownloadLot, self).delete(*args, **kwargs)


class Freight(models.Model):
    class Meta:
        verbose_name = 'Flete'
        verbose_name_plural = 'Fletes'
        ordering = ['-lot__datetime_download_started']

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    lot = models.OneToOneField(Lot, on_delete=models.PROTECT, verbose_name='Lote', blank=False, null=False,
                               related_name='freight_lot')
    cost_unit = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Costo por unidad', default=0)
    boxes_not_paid = models.IntegerField(verbose_name='Jabas no pagadas', default=0)
    cost_false = models.DecimalField(max_digits=7, decimal_places=2, blank=True, verbose_name='Costo falso', default=0,
                                     editable=False)
    total_cost = models.DecimalField(max_digits=7, decimal_places=2, blank=True, verbose_name='Costo total', default=0,
                                     editable=False)

    def __str__(self):
        return f'{self.lot.lot} - {self.total_cost}'

    def save(self, *args, **kwargs):
        self.cost_false = round(self.boxes_not_paid * self.cost_unit if self.boxes_not_paid > 0 else 0, 2)
        cost_shipping = self.lot.boxes * self.cost_unit if self.lot.boxes > 0 else 0
        self.total_cost = self.cost_false + cost_shipping
        detraction = round(float(self.total_cost) * 0.04 if self.total_cost > 0 else 0, 2)
        self.total_cost = float(self.total_cost) - detraction
        self.lot.freight = self.total_cost
        self.lot.save()
        super(Freight, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.lot.freight = 0
        self.lot.save()
        super(Freight, self).delete(using, keep_parents)


class Output(models.Model):
    destine_choices = (('P', 'Producción'), ('M', 'Merma'), ('I', 'I+D'),)

    class Meta:
        verbose_name = 'Salida de Lotes'
        verbose_name_plural = 'Salidas de Lotes'
        ordering = ['date']
        unique_together = ('date', 'lot', 'destine')

    date = models.DateField(verbose_name="Fecha de salida", default=timezone.now, blank=False, null=False)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, verbose_name="Lote", related_name="output")
    kg = models.FloatField(default=0, verbose_name="Kg")
    destine = models.CharField(max_length=1, choices=destine_choices, verbose_name="Destino", blank=False, null=False,
                               default='P')
    history = HistoricalRecords()

    def update_stock(self):
        self.lot.stock = self.lot.calc_stock()
        self.lot.save()

    def save(self, *args, **kwargs):
        super(Output, self).save(*args, **kwargs)
        self.update_stock()

    def delete(self, *args, **kwargs):
        super(Output, self).delete(*args, **kwargs)
        self.update_stock()

    def __str__(self):
        return self.date.strftime('%d/%m/%Y') + "  -  " + self.lot.lot + " - " + str(self.kg)


class ItemsProxy(models.Model):
    class Meta:
        ordering = ["name"]
        abstract = True

    units_choices = (
        ('UN', 'UN'), ('KG', 'KG'), ('LT', 'LT'), ('M2', 'M2'), ('M3', 'M3'), ('M', 'M'), ('CM', 'CM'), ('RL', 'RL'),)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=200, verbose_name="Nombre", blank=False, null=False, unique=True)
    sap = models.CharField(max_length=20, verbose_name='Código SAP', blank=False, null=False, unique=True)
    group = models.ForeignKey(Category, verbose_name='Grupo de producto', blank=False, null=False,
                              on_delete=models.PROTECT, related_name='%(class)s_group')
    unit_of_measurement = models.CharField(max_length=2, choices=units_choices, verbose_name='Unidad de Medida',
                                           blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Material(ItemsProxy):
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'

    def __str__(self):
        return self.name


class ItemsReceipt(models.Model):
    class Meta:
        verbose_name = 'Ingreso de materiales'
        verbose_name_plural = 'Ingresos de materiales'
        ordering = ['-arrival_date']

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    item = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name='Material', blank=False, null=False)
    po_number = models.CharField(verbose_name='Número de orden de compra', max_length=50, blank=False, null=False)
    po_date = models.DateField(verbose_name='Fecha de orden de compra', default=timezone.now)
    arrival_date = models.DateField(verbose_name='Fecha de llegada', blank=False, null=False)
    supplier = models.ForeignKey(MaterialSupplier, on_delete=models.PROTECT, verbose_name='Proveedor', blank=False,
                                 null=False)
    invoice = models.CharField(max_length=30, verbose_name='Factura', blank=True, null=True)
    manufacturing = models.ForeignKey(ManufacturingCompany, on_delete=models.PROTECT, verbose_name='Planta de proceso',
                                      blank=False, null=False)
    quantity = models.IntegerField(verbose_name='Cantidad', blank=False, null=False)
    price_per_unit = models.DecimalField(verbose_name='Precio unitario', max_digits=7, decimal_places=2, default=0)

    stock = models.IntegerField(verbose_name='Stock', blank=True, null=True, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.item.name} - {self.quantity}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.stock = self.quantity
        super(ItemsReceipt, self).save(*args, **kwargs)

    def calc_stock(self):
        try:
            output = sum(output.quantity for output in self.issue.all())
            print(output)
            self.stock = self.quantity - output
            self.save()
        except Exception as e:
            pass


class ItemsIssue(models.Model):
    class Meta:
        verbose_name = 'Salida de materiales'
        verbose_name_plural = 'Salidas de materiales'
        ordering = ['-date']

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    item = models.ForeignKey(ItemsReceipt, on_delete=models.PROTECT, verbose_name='Item', blank=False, null=False,
                             related_name='issue')
    area = models.ForeignKey(Departments, on_delete=models.PROTECT, verbose_name='Departamento', blank=False,
                             null=False)
    date = models.DateField(verbose_name='Fecha', default=timezone.now, blank=False, null=False)
    quantity = models.IntegerField(verbose_name='Cantidad', blank=False, null=False)
    lot_id = models.CharField(max_length=13, verbose_name='Lote', blank=True, null=True)
    manufacturing = models.ForeignKey(ManufacturingCompany, on_delete=models.PROTECT, verbose_name='Planta de proceso',
                                      blank=False, null=False)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.item.item.name} - {self.quantity}'


@receiver(post_save, sender=ItemsIssue)
@receiver(post_delete, sender=ItemsIssue)
def update_stock(sender, instance, **kwargs):
    instance.item.calc_stock()


GLP_CHOICES = (('A', 'Abastecimiento'), ('C', 'Consumo'),)


class GLP(models.Model):
    class Meta:
        verbose_name = 'GLP'
        verbose_name_plural = 'GLP'

    date = models.DateField(verbose_name='Fecha', default=timezone.now, blank=False, null=False, unique=True)
    consumption = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Consumo', blank=False, null=True,
                                      default=0)
    cost = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Costo', blank=False, null=True, default=0)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.date)
