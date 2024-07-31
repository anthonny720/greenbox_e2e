from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget, TimeWidget

from .models import Position, Departments, Staff


class StaffResource(resources.ModelResource):
    position = fields.Field(
        column_name='position',
        attribute='position',
        widget=ForeignKeyWidget(Position, 'nombre_del_campo'))
    area = fields.Field(
        column_name='area',
        attribute='area',
        widget=ForeignKeyWidget(Departments, 'nombre_del_campo'))
    birthday = fields.Field(
        column_name='birthday',
        attribute='birthday',
        widget=DateWidget('%Y-%m-%d'))  # Asegúrate de que el formato coincide con el de tu archivo de importación
    date_of_admission = fields.Field(
        column_name='date_of_admission',
        attribute='date_of_admission',
        widget=DateWidget('%Y-%m-%d'))
    date_of_farewell = fields.Field(
        column_name='date_of_farewell',
        attribute='date_of_farewell',
        widget=DateWidget('%Y-%m-%d'))
    # Ajusta los siguientes campos según el formato esperado en tu archivo de importación
    overtime_hours = fields.Field(
        column_name='overtime_hours',
        attribute='overtime_hours',
        widget=TimeWidget('%H:%M:%S'))
    hours_per_day = fields.Field(
        column_name='hours_per_day',
        attribute='hours_per_day',
        widget=TimeWidget('%H:%M'))
    hours_saturday = fields.Field(
        column_name='hours_saturday',
        attribute='hours_saturday',
        widget=TimeWidget('%H:%M'))
    hours_sunday = fields.Field(
        column_name='hours_sunday',
        attribute='hours_sunday',
        widget=TimeWidget('%H:%M'))

    class Meta:
        model = Staff
        skip_unchanged = True
        report_skipped = False
        # Especifica aquí todos los campos que deseas importar/exportar
        import_id_fields = ('dni',)
        fields = (
        'id', 'name', 'last_name', 'full_name', 'dni', 'photo', 'email', 'status', 'phone', 'position', 'birthday',
        'date_of_admission', 'date_of_farewell', 'area', 'overtime_hours', 'trusted', 'hours_per_day', 'hours_saturday',
        'hours_sunday')
