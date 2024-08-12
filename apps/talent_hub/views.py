from datetime import datetime, date

from apps.user.models import Departments
from apps.user.serializers import DepartmentWithChildrenSerializer
from django.db import DatabaseError
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Staff, Tracking
from .serializers import (TrackingSerializer)


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
                    tracking = Tracking(staff=user, check_in=datetime.now())
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
