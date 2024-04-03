import uuid

from apps.logistic.models import Lot
from django.db import models
from django.db.models import Sum, F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Cuts(models.Model):
    class Meta:
        verbose_name = 'Corte'
        verbose_name_plural = 'Cortes'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name='Nombre')

    def __str__(self):
        return self.name


class BaseConditioning(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(verbose_name='Fecha de Acondicionamiento')
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, verbose_name='Lote')
    cut = models.ForeignKey(Cuts, on_delete=models.PROTECT, verbose_name='Corte', blank=True, null=True)
    logistic_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Logístico')
    rejected_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Rechazado')
    process_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Procesado', default=0,
                                     editable=False)
    enabled_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Habilitado', default=0,
                                     editable=False)
    brix = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Brix')
    ph = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='Ph')
    people = models.PositiveIntegerField(verbose_name='Personas')
    duration = models.DecimalField(verbose_name='Duración',  blank=True, null=True, default=0, max_digits=4,decimal_places=2)
    number_changes = models.PositiveIntegerField(verbose_name='Número de Cambios', default=0)

    class Meta:
        abstract = True
        ordering = ['date', 'id']

    def save(self, *args, **kwargs):
        if self.id and not self._state.adding:
            self.number_changes += 1
        super().save(*args, **kwargs)


class ConditioningPineapple(BaseConditioning):
    crown_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Corona')
    shell_trunk_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Cascara y Tronco')
    pulp_juice_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Pulpa y Jugo')

    class Meta:
        verbose_name_plural = 'Acondicionamiento de Piña'

    def save(self, *args, **kwargs):
        self.process_kg = self.logistic_kg - self.rejected_kg
        self.enabled_kg = self.process_kg - (self.crown_kg + self.shell_trunk_kg + self.pulp_juice_kg)
        super().save(*args, **kwargs)


class ConditioningSweetPotato(BaseConditioning):
    waste_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Desecho')

    class Meta:
        verbose_name_plural = 'Acondicionamiento de Camote'

    def save(self, *args, **kwargs):
        self.process_kg = self.logistic_kg - self.rejected_kg
        self.enabled_kg = self.process_kg - self.waste_kg
        super().save(*args, **kwargs)


@receiver(post_save, sender=ConditioningPineapple)
@receiver(post_save, sender=ConditioningSweetPotato)
@receiver(post_delete, sender=ConditioningPineapple)
@receiver(post_delete, sender=ConditioningSweetPotato)
def dispatch_after_conditioning_change(sender, instance, **kwargs):
    instance.lot.calc_weight_reject()


def get_file_path(instance, filename):
    file = f'lot/{instance.lot.lot}/process/{filename}'
    return file


class ThumbnailProcess(models.Model):
    class Meta:
        verbose_name = 'Fotografía de Proceso'
        verbose_name_plural = 'Fotografías de Proceso'

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    photo = models.ImageField(upload_to=get_file_path, verbose_name='Fotografia', blank=False, null=False)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, verbose_name='Lote', blank=True, null=True,
                            related_name='thumbnail_lot')

    def __str__(self):
        return self.photo.name

    def get_absolute_url(self):
        return self.photo.url if self.photo else ''


@receiver(post_delete, sender=ThumbnailProcess)
def post_delete_file(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)


class PackingLot(models.Model):
    class Meta:
        verbose_name = 'Empaque de Lote'
        verbose_name_plural = 'Empaque de Lotes'
        ordering = ['date_production', 'id']

    categories = (('A', 'A'), ('B', 'B'), ('C', 'C'), ('Q', 'Q'), ('M', 'M'),)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    date_production = models.DateField(verbose_name='Fecha de Producción')
    date_packaging = models.DateField(verbose_name='Fecha de Empaque', blank=True, null=True)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, verbose_name='Lote', blank=True, null=True)

    cut = models.ForeignKey(Cuts, on_delete=models.PROTECT, verbose_name='Corte', blank=True, null=True)
    category = models.CharField(max_length=1, choices=categories, verbose_name='Categoría', default='A')
    kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg', default=0)
    humidity = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Humedad', default=0)
    people = models.PositiveIntegerField(verbose_name='Personas', default=0)
    duration = models.DecimalField(verbose_name='Duración', blank=True, null=True, default=0, max_digits=4,
                                   decimal_places=2)

    process_kg_real = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Procesado reales',
                                          default=0, )
    process_kg = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Kg Procesado', default=0,
                                     editable=False)

    number_changes = models.PositiveIntegerField(verbose_name='Número de Cambios', default=0)

    def save(self, *args, **kwargs):
        if self.id and not self._state.adding:
            self.number_changes += 1
        super().save(*args, **kwargs)


@receiver(post_save, sender=PackingLot)
def dispatch_after_packing(sender, instance, **kwargs):
    try:
        process_model = ConditioningPineapple if instance.lot.product.name == 'Piña' else ConditioningSweetPotato

        lots = PackingLot.objects.filter(lot=instance.lot, date_production=instance.date_production)
        process_instances = process_model.objects.filter(lot=instance.lot, date=instance.date_production)
        updated_lots = []
        for lot in lots:
            specific_process_instances = process_instances.filter(cut=lot.cut) if lot.cut else process_instances
            kg = specific_process_instances.aggregate(total=Sum('process_kg'))['total'] or 0

            if kg:
                total_kg = (lots.filter(cut=lot.cut).aggregate(total=Sum('kg'))['total'] if lot.cut else
                            lots.aggregate(total=Sum('kg'))['total'])

                if total_kg:
                    lot.process_kg = F('kg') / total_kg * kg
                    updated_lots.append(lot)

        if updated_lots:
            PackingLot.objects.bulk_update(updated_lots, ['process_kg'])
    except Exception as e:
        pass
