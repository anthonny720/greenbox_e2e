from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AnalysisPineapple, AnalysisSweetPotato
from .serializers import AnalysisPineappleSerializer, AnalysisSweetPotatoSerializer


# Create your views here.
class AnalysisListView(APIView):
    def get(self, request,model_name):
        if not model_name:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)
        if model_name == 'Piña':
            self.model = AnalysisPineapple
            self.serializer_class = AnalysisPineappleSerializer
        elif model_name == 'Camote':
            self.model = AnalysisSweetPotato
            self.serializer_class = AnalysisSweetPotatoSerializer
        else:
            return Response({'error': 'No se encontró el modelo solicitado.'}, status=status.HTTP_400_BAD_REQUEST)

        lot = request.query_params.get('lot')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        week = request.query_params.get('week')
        if not year:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.model.objects.filter(lot__datetime_download_started__year=year)

        if lot:
            queryset = queryset.filter(lot__lot__icontains=lot)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(lot__datetime_download_started__month=month)
        else:
            if week and week.isdigit() and 1 <= int(week) <= 52:
                queryset = queryset.filter(lot__datetime_download_started__week=week)
            else:
                queryset = queryset.order_by('-lot__datetime_download_started')[0:50]
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class AnalysisDetailView(APIView):
    def get(self, request, model_name, pk):
        if not model_name or not pk:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)
        if model_name == 'Piña':
            model = AnalysisPineapple
            serializer_class = AnalysisPineappleSerializer
        elif model_name == 'Camote':
            model = AnalysisSweetPotato
            serializer_class = AnalysisSweetPotatoSerializer
        else:
            return Response({'error': 'No se encontró el modelo solicitado.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            queryset = model.objects.get(lot__lot=pk)
        except model.DoesNotExist:
            return Response({'error': 'No se encontró el modelo solicitado.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializer_class(queryset)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)