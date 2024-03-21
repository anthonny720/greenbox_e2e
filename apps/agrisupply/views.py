from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Parcel
from .serializers import ParcelSerializer


# Create your views here.


class ParcelListAPIView(APIView):
    model = Parcel
    serializer_class = ParcelSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.model.objects.all()
        sts = request.query_params.get('sts')
        name = request.query_params.get('name')
        provider = request.query_params.get('provider')
        product = request.query_params.get('product')

        if not any([sts, name, provider, product]):
            queryset = queryset[:50]

        if sts == 'P':
            queryset = queryset.filter(status__iexact='P')
        if sts == 'C':
            queryset = queryset.filter(status__iexact='C')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if provider:
            queryset = queryset.filter(provider__id=provider)
        if product:
            queryset = queryset.filter(product__id=product)

        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Parcela creada exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ParcelDetailAPIView(APIView):
    model = Parcel
    serializer_class = ParcelSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Parcela no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Parcela actualizada exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; \n'.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Parcela no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Parcela eliminada exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)
