import requests
from core import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import ProtectedError


from .models import (RawMaterialSupplier, MaterialSupplier, Client, TransportationCompany, ManufacturingCompany)
from .serializers import (RawMaterialSupplierSerializer, MaterialSupplierSerializer, ClientSerializer,
                          TransportationCompanySerializer, ManufacturingCompanySerializer)


class BaseModelListAPIView(APIView):
    model = None
    serializer_class = None

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        if name:
            items = self.model.objects.filter(name__icontains=name)
            serializer = self.serializer_class(items, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        items = self.model.objects.all()
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        ruc = self.request.data.get('ruc')
        config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
        response = requests.get(f'https://api.apis.net.pe/v2/sunat/ruc?numero={ruc}', **config)
        if self.request.data.get('name') == "":
            name = ''
            if response.status_code == 200:
                name = response.json().get('razonSocial')
            self.request.data['name'] = name
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class BaseModelUpdateAPIView(APIView):
    model = None
    serializer_class = None

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


class BaseModelDeleteAPIView(APIView):
    model = None

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            item.delete()
            return Response({'message': 'Registro eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RawMaterialSupplierListAPIView(BaseModelListAPIView):
    model = RawMaterialSupplier
    serializer_class = RawMaterialSupplierSerializer


class RawMaterialSupplierUpdateAPIView(BaseModelUpdateAPIView):
    model = RawMaterialSupplier
    serializer_class = RawMaterialSupplierSerializer


class RawMaterialSupplierDeleteAPIView(BaseModelDeleteAPIView):
    model = RawMaterialSupplier


class MaterialSupplierListAPIView(BaseModelListAPIView):
    model = MaterialSupplier
    serializer_class = MaterialSupplierSerializer


class MaterialSupplierUpdateAPIView(BaseModelUpdateAPIView):
    model = MaterialSupplier
    serializer_class = MaterialSupplierSerializer


class MaterialSupplierDeleteAPIView(BaseModelDeleteAPIView):
    model = MaterialSupplier


class ClientListAPIView(BaseModelListAPIView):
    model = Client
    serializer_class = ClientSerializer


class ClientUpdateAPIView(BaseModelUpdateAPIView):
    model = Client
    serializer_class = ClientSerializer


class ClientDeleteAPIView(BaseModelDeleteAPIView):
    model = Client


class TransportationCompanyListAPIView(BaseModelListAPIView):
    model = TransportationCompany
    serializer_class = TransportationCompanySerializer


class TransportationCompanyUpdateAPIView(BaseModelUpdateAPIView):
    model = TransportationCompany
    serializer_class = TransportationCompanySerializer


class TransportationCompanyDeleteAPIView(BaseModelDeleteAPIView):
    model = TransportationCompany


class ManufacturingCompanyListAPIView(BaseModelListAPIView):
    model = ManufacturingCompany
    serializer_class = ManufacturingCompanySerializer


class ManufacturingCompanyUpdateAPIView(BaseModelUpdateAPIView):
    model = ManufacturingCompany
    serializer_class = ManufacturingCompanySerializer


class ManufacturingCompanyDeleteAPIView(BaseModelDeleteAPIView):
    model = ManufacturingCompany
