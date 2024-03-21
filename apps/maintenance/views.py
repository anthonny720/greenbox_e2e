from django.contrib.auth import get_user_model
from django.db.models import Prefetch, ProtectedError, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (FixedAsset, PhysicalAsset, Tool, Failure, Type, Requirements, WorkOrder, ResourceItem, HelperItem,
                     H2O, Chlorine, )
from .serializers import (FixedAssetSerializer, PhysicalAssetSerializer, ToolsSerializer, FailureSerializer,
                          TypeSerializer, RequirementsSerializer, WorkOrderSerializer, H2OSerializer,
                          ChlorineSerializer, )

User = get_user_model()


# Create your views here.

# Assets
class ListTreeView(APIView):
    def get(self, request):
        obj, created = H2O.objects.get_or_create(date=timezone.now())
        obj, created = Chlorine.objects.get_or_create(date=timezone.now())
        physicals_qs = PhysicalAsset.objects.order_by('name')

        fixed_assets = FixedAsset.objects.prefetch_related(Prefetch('physicals', queryset=physicals_qs)).order_by(
            'name')

        data = [{'name': fix.name, 'id': fix.id,
                 'children': [{'name': physical.name, 'id': physical.id, } for physical in fix.physicals.all()]} for fix
                in fixed_assets]

        return Response({'data': data}, status=status.HTTP_200_OK)


class AbstractListAPIView(APIView):
    model = None
    serializer_class = None
    label = None

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        if name:
            items = self.model.objects.filter(name__icontains=name)
            serializer = self.serializer_class(items, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        items = self.model.objects.all()[0:50]
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'{self.label} exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class AbstractDetailAPIView(APIView):
    model = None
    serializer_class = None
    label = None
    label_delete = None
    label_error = None

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': f'{self.label_error} no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'{self.label} exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': f'{self.label_error} no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': f'{self.label_delete}  exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FixedAssetListAPIView(AbstractListAPIView):
    model = FixedAsset
    serializer_class = FixedAssetSerializer
    label = 'Activo '


class FixedAssetDetailAPIView(AbstractDetailAPIView):
    model = FixedAsset
    serializer_class = FixedAssetSerializer
    label = 'Activo  actualizado'
    label_error = 'Activo '
    label_delete = 'Activo  eliminado'


class PhysicalAssetListAPIView(AbstractListAPIView):
    model = PhysicalAsset
    serializer_class = PhysicalAssetSerializer
    label = 'Activo  creado'


class PhysicalAssetDetailAPIView(AbstractDetailAPIView):
    model = PhysicalAsset
    serializer_class = PhysicalAssetSerializer
    label = 'Activo actualizado'
    label_error = 'Activo '
    label_delete = 'Activo  eliminado'


class ToolListAPIView(AbstractListAPIView):
    model = Tool
    serializer_class = ToolsSerializer
    label = 'Herramienta creada'


class ToolDetailAPIView(AbstractDetailAPIView):
    model = Tool
    serializer_class = ToolsSerializer
    label = 'Herramienta actualizada'
    label_error = 'Herramienta'
    label_delete = 'Herramienta eliminada'


class FailureListAPIView(AbstractListAPIView):
    model = Failure
    serializer_class = FailureSerializer

    def get(self, request, *args, **kwargs):
        items = self.model.objects.all()
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class TypeListAPIView(AbstractListAPIView):
    model = Type
    serializer_class = TypeSerializer

    def get(self, request, *args, **kwargs):
        items = self.model.objects.all()
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class RequirementsListAPIView(APIView):
    model = Requirements
    serializer_class = RequirementsSerializer

    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        week = request.query_params.get('week')

        if not year:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.model.objects.filter(date__year=year)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(date__month=month)
        else:
            if week and week.isdigit() and 1 <= int(week) <= 52:
                queryset = queryset.filter(date__week=week)
            else:
                queryset = queryset.filter(date__month=timezone.now().month)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Requerimiento creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class RequirementsDetailAPIView(APIView):
    model = Requirements
    serializer_class = RequirementsSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Requerimiento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Requerimiento actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Requerimiento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Requerimiento eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


# OT
class WorkOrderListView(APIView):
    model = WorkOrder
    serializer_class = WorkOrderSerializer

    def get(self, request):
        try:

            queryset = self.model.objects.all().order_by('-date_start')
            user_id = request.query_params.get('user')
            type_maintenance_id = request.query_params.get('type_')
            physical_id = request.query_params.get('equipment')
            month = request.query_params.get('month')
            year = request.query_params.get('year')
            week = request.query_params.get('week')
            queryset = queryset.filter(date_start__year=year)
            if user_id:
                user = get_object_or_404(User, pk=user_id)
                queryset = queryset.filter(Q(technical=user) | Q(helpers=user)).distinct()

            if type_maintenance_id:
                queryset = queryset.filter(type_maintenance__id=type_maintenance_id)
            if physical_id:
                queryset = queryset.filter(asset__id=physical_id)
            if month and month.isdigit() and 1 <= int(month) <= 12:
                queryset = queryset.filter(date_start__month=month)
            else:
                if week and week.isdigit() and 1 <= int(week) <= 52:
                    queryset = queryset.filter(date_start__week=week)
                else:
                    queryset = queryset[:50]
            serializer = self.serializer_class(queryset, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Not work orders found', 'detail': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        user = request.user
        if user.position.name in ['Planner de mantenimiento', 'Jefe de mantenimiento'] and 'technical' in request.data:
            technical_id = request.data.get('technical')
            if not User.objects.filter(pk=technical_id).exists():
                return Response({'error': 'Technical user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            request.data['technical'] = user.id
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'OT creada exitosamente'}, status=status.HTTP_201_CREATED)
            else:
                errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
                return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class WorkOrderDetailView(APIView):
    model = WorkOrder
    serializer_class = WorkOrderSerializer

    def patch(self, request, pk):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'OT no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.position.name != 'Planner de mantenimiento' and request.user.position.name != 'Jefe de mantenimiento' and request.user != item.technical:
            return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)
        # if (timezone.now() - work_order.date_start).total_seconds() > 24 * 60 * 60:
        #     return Response({'error': 'No se puede modificar una orden de trabajo pasadas 24 horas de su inicio'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'OT actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'OT no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.position.name != 'Planner de mantenimiento' and request.user.position.name != 'Jefe de mantenimiento' and request.user != item.technical:
            return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)
        # if (timezone.now() - work_order.date_start).total_seconds() > 24 * 60 * 60:
        #     return Response({'error': 'No se puede modificar una orden de trabajo pasadas 24 horas de su inicio'}, status=status.HTTP_403_FORBIDDEN)
        try:
            item.delete()
            return Response({'message': 'OT eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateWorkSupervisorView(APIView):
    model = WorkOrder
    serializer_class = WorkOrderSerializer

    def patch(self, request, pk, *args, **kwargs):

        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'OT no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        item.cleaned = True
        item.supervisor = request.user
        item.save()
        return Response({'message': 'OT validado exitosamente.'}, status=status.HTTP_200_OK)


class UpdateWorkRequesterView(APIView):
    model = WorkOrder
    serializer_class = WorkOrderSerializer

    def patch(self, request, pk):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'OT no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        item.validated = True
        item.requester = request.user
        item.save()
        return Response({'message': 'OT validado exitosamente.'}, status=status.HTTP_200_OK)


class AddResourcesOTView(APIView):

    def post(self, request, pk):
        try:
            order = WorkOrder.objects.get(pk=pk)
        except WorkOrder.DoesNotExist:
            return Response({'error': 'OT no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        # if request.user != order.technical and request.user.position.name != 'Planner de mantenimiento' and request.user.position.name != 'Jefe de mantenimiento':
        #     return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)
        # Opcional:
        # if (timezone.now() - order.date_start).total_seconds() > 24 * 60 * 60:
        #     return Response({'error': 'No se puede modificar una orden de trabajo después de 24 horas de su inicio'}, status=status.HTTP_403_FORBIDDEN)

        ResourceItem.objects.create(work_order=order, article=request.data.get('article'),
                                    quantity=request.data.get('quantity'))
        return Response({'message': 'Recurso añadido exitosamente'}, status=status.HTTP_201_CREATED)


class DeleteResourceOTView(APIView):
    def delete(self, request, pk):
        try:
            item = ResourceItem.objects.get(pk=pk)
        except ResourceItem.DoesNotExist:
            return Response({'error': 'Recurso no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != item.work_order.technical and request.user.position.name != 'Planner de mantenimiento' and request.user.position.name != 'Jefe de mantenimiento':
            return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)
        try:
            item.delete()
            return Response({'message': 'Recurso eliminado existosamente'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el recurso: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AddHelpersOTView(APIView):
    def post(self, request, pk):
        try:
            order = WorkOrder.objects.get(pk=pk)
        except WorkOrder.DoesNotExist:
            return Response({'error': 'OT no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        helper_id = request.data.get('helper')
        date_start = request.data.get('date_start')
        date_finish = request.data.get('date_finish')

        if not all([helper_id, date_start, date_finish]):
            return Response({'error': 'Missing data for helper, date start, or date finish'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.user != order.technical and request.user.position.name != 'Planner de mantenimiento' and request.user.position.name != 'Jefe de mantenimiento':
            return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)
        # Opcional:
        # if (timezone.now() - order.date_start).total_seconds() > 24 * 60 * 60:
        #     return Response({'error': 'No se puede modificar una orden de trabajo después de 24 horas de su inicio'}, status=status.HTTP_403_FORBIDDEN)
        try:
            helper = User.objects.get(pk=helper_id)
        except User.DoesNotExist:
            return Response({'error': 'Ayudante no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        HelperItem.objects.create(work_order=order, helper=helper, date_start=date_start, date_finish=date_finish)
        return Response({'message': 'Ayudante añadido exitosamente'}, status=status.HTTP_201_CREATED)


class DeleteHelperOTView(APIView):
    def delete(self, request, pk):
        try:
            item = HelperItem.objects.get(pk=pk)
        except HelperItem.DoesNotExist:
            return Response({'error': 'Ayudante no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user != item.work_order.technical and request.user.position.name != 'Planner de mantenimiento' and request.user.position.name != 'Jefe de mantenimiento':
            return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)

        # Opcional: Restricción de tiempo para la eliminación de ayudantes
        # if (timezone.now() - helper_item.work_order.date_start).total_seconds() > 24 * 60 * 60:
        #     return Response({'error': 'No se puede modificar una orden de trabajo después de 24 horas de su inicio'}, status=status.HTTP_403_FORBIDDEN)

        try:
            item.delete()
            return Response({'message': 'Ayudante eliminado existosamente'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar al ayudante: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListTechnicalView(APIView):
    def get(self, request):
        users = User.objects.filter(position__name='Técnico de mantenimiento')
        data = [{'id': user.id, 'name': user.get_full_name(), 'active': user.is_active} for user in users]
        return Response({'data': data}, status=status.HTTP_200_OK)


class H2OListAPIView(APIView):
    model = H2O
    serializer_class = H2OSerializer

    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        week = request.query_params.get('week')

        if not year:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.model.objects.filter(date__year=year)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(date__month=month)
        else:
            if week and week.isdigit() and 1 <= int(week) <= 52:
                queryset = queryset.filter(date__week=week)
            else:
                queryset = queryset.filter(date__month=timezone.now().month)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class H2ODetailAPIView(APIView):
    model = H2O
    serializer_class = H2OSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.position.name != 'Técnico de mantenimiento':
            return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ChlorineListAPIView(APIView):
    model = Chlorine
    serializer_class = ChlorineSerializer

    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        week = request.query_params.get('week')

        if not year:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.model.objects.filter(date__year=year)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(date__month=month)
        else:
            if week and week.isdigit() and 1 <= int(week) <= 52:
                queryset = queryset.filter(date__week=week)
            else:
                queryset = queryset.filter(date__month=timezone.now().month)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class ChlorineDetailAPIView(APIView):
    model = Chlorine
    serializer_class = ChlorineSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.position.name != 'Técnico de mantenimiento':
            return Response({'error': 'No tiene permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)

        request.data['technical'] = self.request.user.id
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)
