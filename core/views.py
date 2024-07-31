import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class SearchRUCView(APIView):

    def get(self, request, ruc, *args, **kwargs):
        if ruc and len(ruc) == 11:
            try:
                config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
                response = requests.get(f'https://api.apis.net.pe/v2/sunat/ruc?numero={ruc}', **config)
                if response.status_code == 200:
                    return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'RUC no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            except requests.exceptions.RequestException as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'message': 'No hay RUC proporcionado'}, status=status.HTTP_400_BAD_REQUEST)


class SearchDNIView(APIView):

    def get(self, request, dni, *args, **kwargs):
        print(dni)
        if dni and len(dni) == 8:
            try:
                config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
                response = requests.get(f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}', **config)
                if response.status_code == 200:
                    return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'DNI no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            except requests.exceptions.RequestException as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'message': 'No hay DNI proporcionado'}, status=status.HTTP_400_BAD_REQUEST)


class SearchDollarView(APIView):

    def get(self, request, date, *args, **kwargs):
        if date and len(date) == 10:
            try:
                config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
                response = requests.get(f'https://api.apis.net.pe/v2/sunat/tipo-cambio?date={date}', **config)
                if response.status_code == 200:
                    return Response(response.json(), status=status.HTTP_200_OK)
                else:
                    return Response({'data': 'Tipo de cambio no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            except requests.exceptions.RequestException as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'data': 'No hay fecha proporcionada'}, status=status.HTTP_400_BAD_REQUEST)
