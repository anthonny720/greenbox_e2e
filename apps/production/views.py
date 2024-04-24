from django.db.models import ProtectedError, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConditioningSweetPotato, ConditioningPineapple, PackingLot, Cuts
from .models import ThumbnailProcess
from .serializers import (ConditioningSweetPotatoSerializer, ConditioningPineappleSerializer, PackingLotSerializer,
                          CutSerializer, )
from .serializers import ThumbnailProcessSerializer


# Create your views here.

class CutsListView(APIView):
    model = Cuts
    serializer_class = CutSerializer

    def get(self, request):
        queryset = self.model.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class ConditioningBaseListView(APIView):
    model = None
    serializer_class = None

    def get(self, request):
        lot = request.query_params.get('lot')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        week = request.query_params.get('week')
        queryset = self.model.objects.filter(date__year=year)
        if lot:
            queryset = queryset.filter(lot__lot__icontains=lot)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(date__month=month)
        else:
            if week and week.isdigit() and 1 <= int(week) <= 52:
                queryset = queryset.filter(date__week=week)
            else:
                queryset = queryset.order_by('-date')[0:50]
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro creado exitosamente'}, status=status.HTTP_201_CREATED)
        else:
            errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
            return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ConditioningDetailView(APIView):
    model = None
    serializer_class = None

    def get(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.filter(lot__lot=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
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
        try:
            item.delete()
            return Response({'message': 'Registro eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar  porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConditioningSweetPotatoListView(ConditioningBaseListView):
    model = ConditioningSweetPotato
    serializer_class = ConditioningSweetPotatoSerializer


class ConditioningSweetPotatoDetailView(ConditioningDetailView):
    model = ConditioningSweetPotato
    serializer_class = ConditioningSweetPotatoSerializer


class ConditioningPineappleListView(ConditioningBaseListView):
    model = ConditioningPineapple
    serializer_class = ConditioningPineappleSerializer


class ConditioningPineappleDetailView(ConditioningDetailView):
    model = ConditioningPineapple
    serializer_class = ConditioningPineappleSerializer


class ThumbnailProcessListView(APIView):
    model = ThumbnailProcess
    serializer_class = ThumbnailProcessSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Fotografia añadida exitosamente'}, status=status.HTTP_201_CREATED)
        else:
            errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
            return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ThumbnailDetailView(APIView):
    model = ThumbnailProcess
    serializer_class = ThumbnailProcessSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.filter(lot__lot=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Fotografia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Fotografia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Fotografia eliminada exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar  porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PackingListView(APIView):
    model = PackingLot
    serializer_class = PackingLotSerializer

    def get(self, request):
        lot = request.query_params.get('lot')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        week = request.query_params.get('week')
        product = request.query_params.get('type')
        queryset = self.model.objects.filter(Q(date_production__year=year) & Q(lot__product__name=product))
        if lot:
            queryset = queryset.filter(lot__lot__icontains=lot)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(date_production__month=month)
        else:
            if week and week.isdigit() and 1 <= int(week) <= 52:
                queryset = queryset.filter(date_production__week=week)
            else:
                queryset = queryset.order_by('-date_production')[0:50]
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro creado exitosamente'}, status=status.HTTP_201_CREATED)
        else:
            errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
            return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class PackingDetailView(APIView):
    model = PackingLot
    serializer_class = PackingLotSerializer

    def patch(self, request, pk):
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
