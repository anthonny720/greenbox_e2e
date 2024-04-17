from datetime import datetime, timedelta, date, time

import requests
from apps.user.models import Departments
from apps.user.serializers import DepartmentWithChildrenSerializer
from django.conf import settings
from django.db import DatabaseError
from django.db.models import Q, Case, When, Value, CharField, DurationField, Count, Sum, F, ExpressionWrapper, fields
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Staff, Absenteeism, Tracking, Holiday
from .serializers import (StaffSerializer, AbsenteeismSerializer, TrackingSerializer, TrackingSummarySerializer)


# Create your views here.

class StaffListAPIView(APIView):
    model = Staff

    serializer_class = StaffSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.model.objects.all()

        full_name = request.query_params.get('full_name')
        active = request.query_params.get('status')
        if active == 'true':
            queryset = queryset.filter(status=True)
        else:
            queryset = queryset.filter(status=False)
        if full_name:
            queryset = queryset.filter(full_name__icontains=full_name)

        serializer = StaffSerializer(queryset, many=True)

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        dni = self.request.data.get('dni')
        config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
        response = requests.get(f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}', **config)
        if self.request.data.get('name') == "":
            name = ''
            last_name = ''
            if response.status_code == 200:
                name = response.json().get('nombres')
                last_name = response.json().get('apellidoPaterno') + ' ' + response.json().get('apellidoMaterno')
            self.request.data['name'] = name
            self.request.data['last_name'] = last_name
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Staff creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class StaffDetailAPIView(APIView):
    model = Staff
    serializer_class = StaffSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Staff no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        dni = self.request.data.get('dni')
        config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
        response = requests.get(f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}', **config)
        if self.request.data.get('name') == "" and self.request.data.get('last_name') == "":
            name = 'Ingrese un nombre'
            last_name = 'y un apellido'
            if response.status_code == 200:
                name = response.json().get('nombres')
                last_name = response.json().get('apellidoPaterno') + ' ' + response.json().get('apellidoMaterno')
            self.request.data['name'] = name
            self.request.data['last_name'] = last_name
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Staff actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; \n'.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({'message': 'Registro eliminado exitosamente.'}, status=status.HTTP_200_OK)


class AbsenteeismListAPIView(APIView):
    model = Absenteeism
    serializer_class = AbsenteeismSerializer

    def get_queryset(self):
        return self.model.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class FindUserAPIView(APIView):
    model = Staff
    serializer_class = StaffSerializer

    def get(self, request, *args, **kwargs):  # Cambiado de post a get
        code = request.query_params.get('code')

        if code:
            code = code.strip()
            user = self.model.objects.filter(code=code).first()
            if user:
                serializer = self.serializer_class(user)
                return Response({'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Código no proporcionado.'}, status=status.HTTP_400_BAD_REQUEST)


class StaffNotTrackingAPIView(APIView):

    def post(self, request, *args, **kwargs):
        date_str = request.data.get('date', None)
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            return Response({'error': 'La fecha es requerida.'}, status=status.HTTP_400_BAD_REQUEST)
        users = Staff.objects.filter(status=True, trusted=False).exclude(
            Q(date_of_farewell__lt=date) | Q(date_of_admission__gt=date))
        staff_ids_with_tracking = Tracking.objects.filter(staff__in=users, date=date).values_list('staff_id', flat=True)

        staff_without_tracking = users.exclude(id__in=staff_ids_with_tracking).values('full_name', 'dni')

        staff_list = list(staff_without_tracking)

        if staff_list:
            return Response({'data': staff_list}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No hay usuarios sin seguimiento para la fecha proporcionada.'},
                            status=status.HTTP_404_NOT_FOUND)


# Tracking
class TrackingSummaryListAPIView(APIView):
    serializer_class = TrackingSummarySerializer
    model = Tracking

    def get(self, request, *args, **kwargs):
        user = request.query_params.get('user')
        date_str = request.query_params.get('date')
        department = request.query_params.get('department')

        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
        queryset = self.model.objects.filter(date=date)

        if user:
            queryset = queryset.filter(staff__full_name__icontains=user)

        if department:
            queryset = queryset.filter(staff__area__id=department)

        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class TrackingListAPIView(APIView):
    serializer_class = TrackingSerializer

    def get(self, request, *args, **kwargs):
        user = request.query_params.get('user')
        date_str = request.query_params.get('date')
        department = request.query_params.get('department')

        queryset = Tracking.objects.all()

        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
        queryset = queryset.filter(date=date)

        if user:
            queryset = queryset.filter(staff__full_name__icontains=user)

        if department:
            queryset = queryset.filter(staff__area__id=department)

        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class TrackingDetailAPIView(APIView):
    model = Tracking
    serializer_class = TrackingSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({'message': 'Registro eliminado exitosamente.'}, status=status.HTTP_200_OK)


class CalendarView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            department_id = request.query_params.get('department')
            user_query = request.query_params.get('user')

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            staff_filter = Q(date_of_farewell__isnull=True) | Q(date_of_farewell__gte=start_date)
            if department_id:
                staff_filter &= Q(area__id=department_id)
            if user_query:
                staff_filter &= Q(full_name__icontains=user_query)

            users = Staff.objects.filter(staff_filter).order_by('name')

            relevant_attendances = Tracking.objects.filter(
                date__range=[start_date, end_date],
                staff__in=users
            ).select_related('staff', 'absenteeism')

            dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
            date_strs = [date.strftime('%Y-%m-%d') for date in dates]

            users_summary = {}

            for user in users:
                user_summary_per_date = []
                for date in dates:
                    attendance = relevant_attendances.filter(staff=user, date=date).first()
                    summary = calculate_user_summary(attendance) if attendance else {}
                    user_summary_per_date.append(summary)
                users_summary[user.get_full_name()] = user_summary_per_date

            data = {'dates': date_strs, 'users_summary': users_summary}
            return Response({'data': data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': 'Error desconocido', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_user_summary(attendance):
    summary = {
        'worked_hours': "00:00",
        'delay_hours': "00:00",
        'overtime_hours': "00:00",
        'compensation_hours': "00:00",
    }

    # Suponiendo que attendance.worked_hours ya es un timedelta
    if attendance.worked_hours:
        summary['worked_hours'] = format_time(attendance.worked_hours)

    # Asegúrate de convertir time a timedelta antes de formatear
    if attendance.delay_hours:
        delay_hours_td = time_to_timedelta(attendance.delay_hours)
        summary['delay_hours'] = format_time(delay_hours_td)

    # Convierte time a timedelta antes de sumar, si es necesario
    if attendance.approved:
        overtime_25_hours_td = time_to_timedelta(attendance.overtime_25_hours)
        overtime_35_hours_td = time_to_timedelta(attendance.overtime_35_hours)
        overtime_hours = sum_timedeltas(overtime_25_hours_td, overtime_35_hours_td)
        summary['overtime_hours'] = format_time(overtime_hours)

    # Similar para compensación
    if attendance.absenteeism and attendance.absenteeism.name == 'Compensación':
        absenteeism_hours_td = time_to_timedelta(attendance.absenteeism_hours)
        summary['compensation_hours'] = format_time(absenteeism_hours_td)

    if attendance.absenteeism_extra and attendance.absenteeism_extra.name == 'Compensación':
        absenteeism_hours_extra_td = time_to_timedelta(attendance.absenteeism_hours_extra)
        compensation_hours_extra = sum_timedeltas(absenteeism_hours_extra_td)
        summary['compensation_hours'] = format_time(compensation_hours_extra)

    return summary


def sum_timedeltas(*args):

    total = timedelta()
    for arg in args:
        if isinstance(arg, time):
            arg_timedelta = timedelta(hours=arg.hour, minutes=arg.minute, seconds=arg.second)
            total += arg_timedelta
        elif isinstance(arg, timedelta):
            total += arg
        else:
            pass
    return total


def format_time(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return '{:02d}:{:02d}'.format(hours, minutes)


def time_to_timedelta(time_obj):
    if time_obj:
        return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)
    else:
        return timedelta()



def format_duration(duration):
    if not duration:
        return "00:00:00"
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}:00"


class SummaryView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            department_id = request.query_params.get('department')
            user_query = request.query_params.get('user')

            if not start_date_str or not end_date_str:
                return Response({"error": "Se requieren la fecha de inicio y la fecha de fin."},
                                status=status.HTTP_400_BAD_REQUEST)

            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            users = Staff.objects.filter(Q(date_of_farewell__isnull=True) | Q(date_of_farewell__gte=start_date))
            if department_id:
                users = users.filter(area_id=department_id)
            if user_query:
                users = users.filter(full_name__icontains=user_query)

            attendances = Tracking.objects.filter(date__range=[start_date, end_date], staff__in=users).annotate(
                is_inasistencia=Case(When(absenteeism__name__in=["Inasistencia", "Suspensión"], then=Value(1)),
                                     default=Value(0), output_field=CharField(), ), is_descanso_semanal=Case(When(
                    absenteeism__name__in=["Descanso semanal", "CONADIS", "Descanso feriado",
                                           "Descanso colaborador mes"], then=Value(1)), default=Value(0),
                    output_field=CharField(), ),
                is_licencia_sin_gose_de_haber=Case(When(absenteeism__name="Licencia sin gose de haber", then=Value(1)),
                                                   default=Value(0), output_field=CharField(), ),
                is_vacaciones=Case(When(absenteeism__name="Vacaciones", then=Value(1)), default=Value(0),
                                   output_field=CharField(), ),

                is_descanso_medico=Case(When(absenteeism__name="Descanso médico", then=Value(1)), default=Value(0),
                                        output_field=CharField(), ),
                approved_overtime_25=Case(When(approved=True, then='overtime_25_hours'), default=Value('00:00:00'),
                                          output_field=DurationField()),
                approved_overtime_35=Case(When(approved=True, then='overtime_35_hours'), default=Value('00:00:00'),
                                          output_field=DurationField()), ).values('staff_id').annotate(
                total_days_worked=Count('id'), inasistencia_sum=Sum('is_inasistencia'),
                descanso_semanal_sum=Sum('is_descanso_semanal'),
                licencia_sin_gose_de_haber_sum=Sum('is_licencia_sin_gose_de_haber'),
                vacaciones_sum=Sum('is_vacaciones'), descanso_medico_sum=Sum('is_descanso_medico'),
                overtime_25_sum=Sum('approved_overtime_25', output_field=DurationField()),
                overtime_35_sum=Sum('approved_overtime_35', output_field=DurationField()), total_worked_night=Sum(
                    Case(When(is_day_shift=False, then=F('worked_hours')),
                         default=ExpressionWrapper(Value(timedelta(seconds=0)), output_field=fields.DurationField()),
                         output_field=fields.DurationField())))

            summary_data = []
            for attendance in attendances:
                user = users.get(id=attendance['staff_id'])
                user_summary = {"user": user.get_full_name(),
                                "overtime_25": format_duration(attendance['overtime_25_sum']),
                                "overtime_35": format_duration(attendance['overtime_35_sum']),
                                "total_worked_night": format_duration(attendance['total_worked_night']),
                                "total_days_worked": attendance['total_days_worked'],
                                "inasistencia": attendance['inasistencia_sum'],
                                "descanso_semanal": attendance['descanso_semanal_sum'],
                                "licencia_sin_gose_de_haber": attendance['licencia_sin_gose_de_haber_sum'],
                                "vacaciones": attendance['vacaciones_sum'],
                                "descanso_medico": attendance['descanso_medico_sum'], }
                summary_data.append(user_summary)

            return Response({"data": summary_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OutsourcingView(APIView):
    def get(self, request, *args, **kwargs):
        try:

            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            if not start_date_str or not end_date_str:
                return Response({"error": "Se requieren la fecha de inicio y la fecha de fin."},
                                status=status.HTTP_400_BAD_REQUEST)

            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            users = Staff.objects.filter(
                Q(date_of_farewell__isnull=True) | Q(date_of_farewell__gte=start_date)
            ).prefetch_related('tracking_staff', 'position').order_by('name')

            summary_data = []

            feriados_en_rango = Holiday.objects.filter(date__range=[start_date, end_date])

            for user in users:
                user_attendances = Tracking.objects.filter(
                    staff=user, date__range=[start_date, end_date]
                ).select_related('absenteeism')

                user_summary = {
                    'user': user.get_full_name(),
                    'dni': user.dni,
                    'position': user.position.name if user.position else '',
                    'out': user.date_of_farewell,
                    'overtime_25': timedelta(0),
                    'overtime_35': timedelta(0),
                    'total_worked_night': timedelta(0),
                    'total_days_worked': 0,
                    'inasistencia': 0,
                    'descanso_semanal': 0,
                    'licencia_sin_gose_de_haber': 0,
                    'vacaciones': 0,
                    'descanso_medico': 0,
                    'feriado': 0,
                    'dias_inasistencia': [],
                    'dias_licencia_sin_gose_de_haber': [],
                    'dias_vacaciones': [],
                    'dias_descanso_medico': [],
                    'dias_feriado': [],
                    'horas_feriado': timedelta(0),
                    'compensación_feriados': timedelta(0),
                }

                for attendance in user_attendances:
                    user_summary['total_days_worked'] += 1

                    if attendance.absenteeism:
                        format_date = attendance.date.strftime('%d/%m')
                        if attendance.absenteeism.name == 'Inasistencia' or attendance.absenteeism.name == 'Suspensión':
                            user_summary['dias_inasistencia'].append(format_date)
                            user_summary['inasistencia'] += 1
                            user_summary['total_days_worked'] -= 1
                        if attendance.absenteeism.name == 'Descanso semanal' or attendance.absenteeism.name == 'CONADIS' or attendance.absenteeism.name == 'Descanso feriado' or attendance.absenteeism.name == 'Descanso colaborador mes':
                            user_summary['descanso_semanal'] += 1
                            user_summary['total_days_worked'] -= 1
                        if attendance.absenteeism.name == 'Licencia sin gose de haber':
                            user_summary['dias_licencia_sin_gose_de_haber'].append(format_date)
                            user_summary['licencia_sin_gose_de_haber'] += 1
                            user_summary['total_days_worked'] -= 1
                        if attendance.absenteeism.name == 'Descanso médico':
                            user_summary['dias_descanso_medico'].append(format_date)
                            user_summary['descanso_medico'] += 1
                            user_summary['total_days_worked'] -= 1
                        if attendance.absenteeism.name == 'Vacaciones':
                            user_summary['dias_vacaciones'].append(format_date)
                            user_summary['vacaciones'] += 1
                            user_summary['total_days_worked'] -= 1
                        if attendance.absenteeism.name == 'Compensación feriados':
                            user_summary['compensación_feriados'] += timedelta(hours=attendance.absenteeism_hours.hour,
                                                                                minutes=attendance.absenteeism_hours.minute) if attendance.absenteeism_hours else timedelta(0)
                            user_summary['total_days_worked'] -= 1
                    if attendance.approved:
                        user_summary['overtime_25'] += timedelta(hours=attendance.overtime_25_hours.hour,
                                                                        minutes=attendance.overtime_25_hours.minute) if attendance.overtime_25_hours else timedelta(0)
                        user_summary['overtime_35'] += timedelta(hours=attendance.overtime_35_hours.hour,
                                                                        minutes=attendance.overtime_35_hours.minute) if attendance.overtime_35_hours else timedelta(0)
                    es_feriado = feriados_en_rango.filter(date=attendance.date).exists()
                    if es_feriado:
                        user_summary['dias_feriado'].append(format_date)
                        user_summary['feriado'] += 1
                        user_summary['horas_feriado'] += attendance.worked_hours

                    user_summary['total_worked_night'] += attendance.worked_hours if not attendance.is_day_shift else timedelta(
                    hours=0)

                user_summary['overtime_25'] = format_duration(user_summary['overtime_25'])
                user_summary['overtime_35'] = format_duration(user_summary['overtime_35'])
                user_summary['horas_feriado'] = format_duration(user_summary['horas_feriado'])
                user_summary['compensación_feriados'] = format_duration(user_summary['compensación_feriados'])
                user_summary['total_worked_night'] = format_duration(user_summary['total_worked_night'])
                summary_data.append(user_summary)

            return Response({'data': summary_data}, status=status.HTTP_200_OK)
        except DatabaseError as e:
            error_message = 'No se puede procesar su solicitud debido a un error de base de datos. Por favor, inténtelo de nuevo más tarde.'
            return Response({'message': error_message, 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            error_message = 'Se ha producido un error inesperado en el servidor. Por favor, inténtelo de nuevo más tarde.'
            return Response({'message': error_message, 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StaffNotTrackingView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            date_str = request.data.get('date', None)
            if date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                tracked_staff_ids = Tracking.objects.filter(date=date).values_list('staff', flat=True)
                staff_without_tracking = Staff.objects.filter(status=True, trusted=False).exclude(
                    id__in=tracked_staff_ids).exclude(date_of_farewell__lt=date).values('full_name', 'id')

                return Response({'data': list(staff_without_tracking)}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'La fecha es obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = f'Se ha producido un error inesperado: {str(e)}'
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FindUserView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            uuid = request.data.get('code')
            if uuid:
                uuid = uuid.strip()
                try:
                    user = Staff.objects.get(dni__icontains=uuid)
                    serializer = StaffSerializer(user, many=False)
                    return Response({'data': serializer.data}, status=status.HTTP_200_OK)
                except Staff.DoesNotExist:
                    return Response({'message': 'No existe el usuario'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message': 'No se ha encontrado el UUID'}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError as e:
            error_message = 'No se puede procesar su solicitud debido a un error de base de datos. Por favor, inténtelo de nuevo más tarde.'
            return Response({'message': error_message, 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(e)
            error_message = 'Se ha producido un error inesperado en el servidor. Por favor, inténtelo de nuevo más tarde.'
            return Response({'message': error_message, 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScannerTrackingView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            code = str(data['code']).strip()
            category = data['attendance'].strip()

            if len(code) != 8:
                return Response({'message': 'El codigo  es invalido'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = Staff.objects.get(dni=code)
            except Staff.DoesNotExist:
                return Response({'message': 'No existe el usuario'}, status=status.HTTP_404_NOT_FOUND)

            tracking_exists = Tracking.objects.filter(staff=user, date=date.today()).first()

            last_tracking = Tracking.objects.filter(staff=user).order_by('-date').first()

            if last_tracking is not None:
                if last_tracking.date:
                    if last_tracking.date != date.today():
                        if last_tracking.absenteeism:
                            pass
                        else:
                            if last_tracking.check_out is None:
                                if last_tracking.is_day_shift == False:
                                    if category == 'lunch_start':
                                        if last_tracking.lunch_start is None:
                                            last_tracking.lunch_start = timezone.now()
                                            last_tracking.save()
                                            serializer = TrackingSerializer(last_tracking, many=False)
                                            return Response({'message': 'Se ha registrado el inicio de almuerzo',
                                                             'data': serializer.data}, status=status.HTTP_201_CREATED)
                                        else:
                                            return Response({'message': 'Ya existe un registro de inicio de almuerzo'},
                                                            status=status.HTTP_400_BAD_REQUEST)
                                    elif category == 'lunch_end':
                                        if last_tracking.lunch_start is None:
                                            return Response({'message': 'Primero debe registrar el inicio de almuerzo'},
                                                            status=status.HTTP_400_BAD_REQUEST)
                                        elif last_tracking.lunch_end is None:
                                            last_tracking.lunch_end = timezone.now()
                                            last_tracking.save()
                                            serializer = TrackingSerializer(last_tracking, many=False)
                                            return Response({'message': 'Se ha registrado el fin de almuerzo',
                                                             'data': serializer.data}, status=status.HTTP_201_CREATED)
                                        else:
                                            return Response({'message': 'Ya existe un registro de fin de almuerzo'},
                                                            status=status.HTTP_400_BAD_REQUEST)
                                    elif category == 'check_out':
                                        if last_tracking.lunch_end is None:
                                            return Response({'message': 'Primero debe registrar el fin de almuerzo '},
                                                            status=status.HTTP_400_BAD_REQUEST)
                                        elif last_tracking.check_out is None:
                                            last_tracking.check_out = timezone.now()
                                            last_tracking.save()
                                            serializer = TrackingSerializer(last_tracking, many=False)
                                            return Response({'message': 'Se ha registrado la salida del usuario',
                                                             'data': serializer.data}, status=status.HTTP_201_CREATED)
                                        else:
                                            return Response({'message': 'Ya existe un registro de salida'},
                                                            status=status.HTTP_400_BAD_REQUEST)
                                    else:
                                        return Response({'message': 'Ya existe un registro de ingreso'},
                                                        status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    last_tracking.check_out = timezone.now()
                                    last_tracking.save()
            if category == 'check_in':
                if not tracking_exists:
                    tracking = Tracking(staff=user, check_in=timezone.now())
                    tracking.save()
                    serializer = TrackingSerializer(tracking, many=False)
                    return Response({'message': 'Se ha registrado la marcación del usuario', 'data': serializer.data},
                                    status=status.HTTP_201_CREATED)
                else:
                    return Response({'message': 'Ya existe un registro de ingreso'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if tracking_exists is None or tracking_exists.check_in is None:
                    return Response({'message': 'Primero debe registrar su ingreso'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif category == 'lunch_start':
                    if tracking_exists.lunch_start is None:
                        tracking_exists.lunch_start = timezone.now()
                        tracking_exists.save()
                        serializer = TrackingSerializer(tracking_exists, many=False)
                        return Response({'message': 'Se ha registrado el inicio de almuerzo', 'data': serializer.data},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message': 'Ya existe un registro de inicio de almuerzo'},
                                        status=status.HTTP_400_BAD_REQUEST)
                elif category == 'lunch_end':
                    if tracking_exists.lunch_start is None:
                        return Response({'message': 'Primero debe registrar el inicio de almuerzo'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    elif tracking_exists.lunch_end is None:
                        tracking_exists.lunch_end = timezone.now()
                        tracking_exists.save()
                        serializer = TrackingSerializer(tracking_exists, many=False)
                        return Response({'message': 'Se ha registrado el fin de almuerzo', 'data': serializer.data},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message': 'Ya existe un registro de fin de almuerzo'},
                                        status=status.HTTP_400_BAD_REQUEST)
                elif category == 'check_out':
                    if tracking_exists.lunch_end is None:
                        return Response({'message': 'Primero debe registrar el fin de almuerzo '},
                                        status=status.HTTP_400_BAD_REQUEST)
                    elif tracking_exists.check_out is None:
                        tracking_exists.check_out = timezone.now()
                        tracking_exists.save()
                        serializer = TrackingSerializer(tracking_exists, many=False)
                        return Response({'message': 'Se ha registrado la salida del usuario', 'data': serializer.data},
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message': 'Ya existe un registro de salida'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'No existe la categoría de marcación'},
                                    status=status.HTTP_400_BAD_REQUEST)

        except DatabaseError as e:
            error_message = 'No se puede procesar su solicitud debido a un error de base de datos. Por favor, inténtelo de nuevo más tarde.'
            return Response({'message': str(e), 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            error_message = 'Se ha producido un error inesperado en el servidor. Por favor, inténtelo de nuevo más tarde.'
            return Response({'message': str(e), 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentListView(APIView):
    model = Departments
    serializer_class = DepartmentWithChildrenSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.model.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
