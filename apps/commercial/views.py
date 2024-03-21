from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Sample
from .serializers import SamplesSerializer


# Create your views here.
class SamplesAPIView(APIView):
    model = Sample
    serializer_class = SamplesSerializer

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        client = request.query_params.get('client')

        if not year:
            return Response({'error': 'year is required'}, status=status.HTTP_400_BAD_REQUEST)

        query = self.model.objects.filter(date__year=year)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            query = query.filter(date__month=month)
        if client:
            query = query.filter(client__icontains=client)
        serializer = self.serializer_class(query, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=self.request.data)
        user = request.user
        serializer.initial_data['applicant'] = user.first_name + ' ' + user.last_name if user else 'Anónimo'
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Muestra creada exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class SamplesDetailAPIView(APIView):
    model = Sample
    serializer_class = SamplesSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Muestra no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Muestra actualizada exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)
