import uuid
from datetime import timedelta, datetime, time

from apps.user.models import Departments, Position
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords


def get_upload_to(instance, filename):
    extension = filename.split('.')[-1]
    return f'staff/{instance.dni}/{instance.id}.{extension}'


class Staff(models.Model):
    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'
        ordering = ['last_name', 'name']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Nombre')
    last_name = models.CharField(max_length=100, verbose_name='Apellido')
    full_name = models.CharField(max_length=100, verbose_name='Nombre completo', blank=True, null=True)
    dni = models.CharField(max_length=8, verbose_name='DNI', unique=True)
    photo = models.ImageField(upload_to=get_upload_to, verbose_name='Foto', blank=True, null=True)
    email = models.EmailField(verbose_name='Correo electrónico', blank=True, null=True)
    status = models.BooleanField(default=True, verbose_name='Estado')
    phone = models.CharField(max_length=10, verbose_name='Teléfono')
    position = models.ForeignKey(Position, on_delete=models.PROTECT, verbose_name='Cargo',
                                 related_name='staff_position')

    birthday = models.DateField(verbose_name='Fecha de nacimiento', blank=True, null=True)
    date_of_admission = models.DateField(verbose_name='Fecha de ingreso', blank=True, null=True)
    date_of_farewell = models.DateField(verbose_name='Fecha de salida', blank=True, null=True)
    area = models.ForeignKey(Departments, on_delete=models.PROTECT, verbose_name='Área', related_name='staff_area')
    overtime_hours = models.DurationField(verbose_name='Horas extras', blank=True, null=True, default='00:00:00')
    trusted = models.BooleanField(default=False, verbose_name='Personal de confianza')
    hours_per_day = models.TimeField(verbose_name='Horas por día', blank=True, null=True, default='08:00:00')
    hours_saturday = models.TimeField(verbose_name='Horas por sábado', blank=True, null=True, default='08:00:00')
    hours_sunday = models.TimeField(verbose_name='Horas por domingo', blank=True, null=True, default='08:00:00')
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name} {self.last_name}'

    def get_full_name(self):
        return f'{self.last_name} {self.name}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_name = f'{self.last_name} {self.name}'
        super(Staff, self).save()


class Absenteeism(models.Model):
    class Meta:
        verbose_name = 'Ausentismo'
        verbose_name_plural = 'Ausentismos'
        ordering = ['name']

    name = models.CharField(max_length=50, verbose_name='Nombre')

    def __str__(self):
        return self.name


class Tracking(models.Model):
    class Meta:
        verbose_name = 'Asistencias'
        verbose_name_plural = 'Asistencias'
        db_table = 'attendance'
        ordering = ['-date', 'staff__name']

    staff = models.ForeignKey(Staff, on_delete=models.PROTECT, verbose_name='Personal', related_name='tracking_staff')
    date = models.DateField(verbose_name='Fecha', blank=True, null=True)
    check_in = models.DateTimeField(verbose_name='Hora de entrada', blank=True, null=True, )
    real_check_in = models.DateTimeField(verbose_name='Hora de entrada real', blank=True, null=True, )
    lunch_start = models.DateTimeField(verbose_name='Inicio de almuerzo', blank=True, null=True, )
    lunch_end = models.DateTimeField(verbose_name='Fin de almuerzo', blank=True, null=True, )
    real_lunch_end = models.DateTimeField(verbose_name='Fin de almuerzo real', blank=True, null=True, )
    check_out = models.DateTimeField(verbose_name='Hora de salida', blank=True, null=True, )
    absenteeism = models.ForeignKey(Absenteeism, on_delete=models.PROTECT, verbose_name='Ausentismo',
                                    related_name='tracking_absenteeism', blank=True, null=True)
    absenteeism_hours = models.TimeField(verbose_name='Horas de ausentismo', blank=True, null=True, default='00:00:00')
    absenteeism_extra = models.ForeignKey(Absenteeism, on_delete=models.PROTECT,
                                          verbose_name='Ausentismo extraordinario',
                                          related_name='tracking_absenteeism_extra', blank=True, null=True)
    absenteeism_hours_extra = models.TimeField(verbose_name='Horas de ausentismo extraordinario', blank=True, null=True,
                                               default='00:00:00')
    worked_hours = models.DurationField(verbose_name='Horas trabajadas', blank=True, null=True)
    overtime_25_hours = models.TimeField(verbose_name='Horas extras 25%', blank=True, null=True, default='00:00:00')
    overtime_35_hours = models.TimeField(verbose_name='Horas extras 35%', blank=True, null=True, default='00:00:00')
    delay_hours = models.TimeField(verbose_name='Horas de retraso', blank=True, null=True, default='00:00:00')
    approved = models.BooleanField(verbose_name='Aprobado', default=False)
    is_day_shift = models.BooleanField(verbose_name='Horario día/noche', default=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.staff} - {self.date}' if self.date else f'{self.staff}'

    def calculate_overtime(self, hours, overtime_limit=timedelta(hours=2, minutes=0, seconds=0)):
        if self.worked_hours > hours:
            overtime_hours = self.worked_hours - hours
            self.overtime_25_hours = min(overtime_limit, overtime_hours)
            self.overtime_35_hours = max(timedelta(0), overtime_hours - overtime_limit)

            datetime_min = datetime.min
            overtime_25_datetime = datetime_min + self.overtime_25_hours
            overtime_35_datetime = datetime_min + self.overtime_35_hours

            # Extraer la parte de tiempo de los objetos datetime
            self.overtime_25_hours = overtime_25_datetime.time().replace(microsecond=0)
            self.overtime_35_hours = overtime_35_datetime.time().replace(microsecond=0)
            self.worked_hours = hours
        else:
            self.overtime_25_hours = time(0).replace(microsecond=0)
            self.overtime_35_hours = time(0).replace(microsecond=0)

    def get_real_worked_hours(self):
        try:
            if self.real_check_in and self.check_out:
                time_real = self.check_out - self.real_check_in
                if self.lunch_start and self.real_lunch_end:
                    lunch_time = self.real_lunch_end - self.lunch_start
                    time_real -= lunch_time
                time_real = time_real - timedelta(microseconds=time_real.microseconds)
                return time_real
            else:
                return '00:00:00'
        except:
            return '00:00:00'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        self.worked_hours = timedelta(hours=0)

        self.delay_hours = '00:00:00'

        try:
            if self.check_in:
                minute = self.check_in.minute
                self.real_check_in = self.check_in
                if minute > 20:
                    self.check_in = self.check_in.replace(hour=self.check_in.hour + 1, minute=0, second=0)
                    self.delay_hours = '00:00:00'
                else:
                    self.delay_hours = '00:{:02d}:00'.format(minute)
        except:
            pass

        if self.lunch_end:
            self.real_lunch_end = self.lunch_end
            if self.lunch_start:
                self.lunch_end = self.lunch_end.replace(hour=self.lunch_start.hour + 1, minute=self.lunch_start.minute,
                                                        second=0)

        if self.check_in and self.check_out:
            time_worked = self.check_out - self.check_in
            if self.lunch_start and self.lunch_end:
                lunch_time = self.lunch_end - self.lunch_start
                time_worked -= lunch_time
            self.worked_hours = time_worked

        if self.absenteeism and self.absenteeism_hours:
            absenteeism_seconds = (
                    self.absenteeism_hours.hour * 3600 + self.absenteeism_hours.minute * 60 + self.absenteeism_hours.second)
            self.worked_hours += timedelta(seconds=absenteeism_seconds)

        if self.absenteeism_extra and self.absenteeism_hours_extra:
            absenteeism_extra_seconds = (
                    self.absenteeism_hours_extra.hour * 3600 + self.absenteeism_hours_extra.minute * 60 + self.absenteeism_hours_extra.second)
            self.worked_hours += timedelta(seconds=absenteeism_extra_seconds)

        try:
            # Calculate overtime
            if self.check_in and self.check_out:
                if self.date.strftime('%A') == 'Saturday':
                    self.calculate_overtime(
                        timedelta(hours=self.staff.hours_saturday.hour, minutes=self.staff.hours_saturday.minute))
                elif self.date.strftime('%A') == 'Sunday':
                    self.calculate_overtime(
                        timedelta(hours=self.staff.hours_sunday.hour, minutes=self.staff.hours_sunday.minute))
                else:
                    self.calculate_overtime(
                        timedelta(hours=self.staff.hours_per_day.hour, minutes=self.staff.hours_per_day.minute))
        except:
            pass
        try:
            self.worked_hours = self.worked_hours - timedelta(microseconds=self.worked_hours.microseconds)
        except:
            pass

        if self.check_in:
            if timezone.is_naive(self.check_in):
                # Convertir a "aware" usando la zona horaria por defecto del proyecto
                self.check_in = timezone.make_aware(self.check_in, timezone.get_default_timezone())
                # Extraer la fecha en la zona horaria local
            self.date = timezone.localtime(self.check_in).date()

        try:
            if 5 <= self.check_in.hour < 18:
                self.is_day_shift = True
            else:
                self.is_day_shift = False
        except:
            pass

        super().save(force_insert, force_update, using, update_fields)


@receiver(pre_save, sender=Staff)
def pre_save_photo(sender, instance, **kwargs):
    if not instance.id:
        return
    try:
        old_file = sender.objects.get(pk=instance.pk).photo
        old_file.delete(save=False)
        new_file = instance.photo
    except sender.DoesNotExist:
        pass


@receiver(post_delete, sender=Staff)
def post_delete_photo(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)


class Holiday(models.Model):
    class Meta:
        verbose_name = 'Feriado'
        verbose_name_plural = 'Feriados'
        db_table = 'holidays'
        ordering = ['date']

    date = models.DateField(verbose_name='Fecha', blank=True, null=True)
    name = models.CharField(verbose_name='Nombre', max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.date}'
