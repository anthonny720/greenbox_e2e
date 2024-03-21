from datetime import timedelta

import requests
from core import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import ProtectedError, Q, Sum, F
from django.utils import timezone
from apps.quality_control.models import (AnalysisPineapple, AnalysisSweetPotato, )
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client

from .models import (ExternalPeople, Lot, DownloadLot, Pallets, ItemsLot, Output, Material, ItemsIssue, ItemsReceipt,
                     Freight, GLP, Files, )
from .serializers import (ExternalPeopleSerializer, LotSummarySerializer, LotSerializer, DownloadLotSerializer,
                          PalletsSerializer, ItemsLotSerializer, OutputSerializer, MaterialSerializer,
                          ItemsIssueSerializer, ItemsReceiptSerializer, FreightSerializer, GLPSerializer,
                          FilesSerializer, )

User = get_user_model()


# Create your views here.
class ExternalPersonListAPIView(APIView):
    model = ExternalPeople
    serializer_class = ExternalPeopleSerializer

    def get(self, request, *args, **kwargs):
        full_name = request.query_params.get('full_name')
        if full_name:
            items = self.model.objects.filter(full_name__icontains=full_name)
            serializer = self.serializer_class(items, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        items = self.model.objects.all()[0:50]
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        dni = self.request.data.get('dni')
        config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
        response = requests.get(f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}', **config)
        if self.request.data.get('full_name') == "":
            full_name = 'Pendiente de actualización'
            if response.status_code == 200:
                name = response.json().get('nombres')
                last_name = response.json().get('apellidoPaterno') + ' ' + response.json().get('apellidoMaterno')
            self.request.data['full_name'] = name + ' ' + last_name
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Externo creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ExternalPersonUpdateAPIView(APIView):
    model = ExternalPeople
    serializer_class = ExternalPeopleSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Externo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        dni = self.request.data.get('dni')
        config = {'headers': {"Authorization": f'Bearer ${settings.TOKEN_RENIEC}'}}
        response = requests.get(f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}', **config)
        if self.request.data.get('full_name') == "":
            full_name = 'Pendiente de actualización'
            if response.status_code == 200:
                name = response.json().get('nombres')
                last_name = response.json().get('apellidoPaterno') + ' ' + response.json().get('apellidoMaterno')
            self.request.data['full_name'] = name + ' ' + last_name
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Externo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Externo eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LotListAPIView(APIView):
    model = Lot
    serializer_class = LotSummarySerializer

    def get(self, request, *args, **kwargs):
        obj, created = GLP.objects.get_or_create(date=timezone.now())
        lot = request.query_params.get('lot')
        company = request.query_params.get('company')
        query = self.model.objects.all()

        query_filter = Q()
        if lot or company:
            if lot:
                query_filter &= Q(lot__icontains=lot)
            if company:
                query_filter &= Q(manufacturing=company)
            items_query = query.filter(query_filter)
        else:
            items_query = query

        stock_by_product = items_query.values('product__name').annotate(total_stock=Sum('stock')).order_by(
            'product__name')

        items = items_query.order_by('-datetime_download_started')[:50]

        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data, 'stock_by_product': list(stock_by_product)},
                        status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = LotSerializer(data=self.request.data)
        if serializer.is_valid():
            lot_instance = serializer.save()
            if serializer.validated_data.get('product').name == 'Piña':
                product_name = serializer.validated_data.get('product').name
                if product_name == 'Piña':
                    AnalysisPineapple.objects.get_or_create(lot=lot_instance)
                elif product_name == 'Camote':
                    AnalysisSweetPotato.objects.get_or_create(lot=lot_instance)
                else:
                    pass
            return Response({'message': 'Lote creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class LotDetailAPIView(APIView):
    model = Lot
    serializer_class = LotSerializer

    def get(self, request, lot, *args, **kwargs):
        try:
            item = self.model.objects.get(lot=lot)
        except self.model.DoesNotExist:
            return Response({'error': 'Lote no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(item, many=False)
        signature = []
        boss = User.objects.filter(position__name='Jefe de logistica y compras').first()
        manager = User.objects.filter(position__name='Gerente de administracion y finanzas').first()
        boss_production = User.objects.filter(position__name='Jefe de producción').first()

        if boss and manager and boss_production:
            signature.append({'name': boss.get_full_name(), 'email': boss.email, 'signature': boss.get_signature_url()})
            signature.append(
                {'name': manager.get_full_name(), 'email': manager.email, 'signature': manager.get_signature_url()})
            signature.append({'name': boss_production.get_full_name(), 'email': boss_production.email,
                              'signature': boss_production.get_signature_url()})
        else:
            signature.append({'name': '', 'email': '', 'signature': ''})
            signature.append({'name': '', 'email': '', 'signature': ''})
            signature.append({'name': '', 'email': '', 'signature': ''})

        return Response({'data': serializer.data, 'signature': signature}, status=status.HTTP_200_OK)

    def patch(self, request, lot, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=lot)
        except self.model.DoesNotExist:
            return Response({'error': 'Lote no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Lote actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


# Service Download

class DownloadLotListAPIView(APIView):
    model = DownloadLot
    serializer_class = DownloadLotSerializer

    def get(self, request, *args, **kwargs):
        lot = request.query_params.get('lot')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        query = self.model.objects.all()
        if lot:
            query = query.filter(lot__lot__icontains=lot)
        if year:
            query = query.filter(lot__datetime_download_started__year=year)
        if month:
            query = query.filter(lot__datetime_download_started__month=month)
        else:
            query = query.filter(lot__datetime_download_started__month=timezone.now().month)

        serializer = self.serializer_class(query, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        if DownloadLot.objects.filter(lot=self.request.data.get('lot')).exists():
            return Response({'error': 'El lote ya fue registrado.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Registro creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class FreightListAPIView(APIView):
    model = Freight
    serializer_class = FreightSerializer

    def get(self, request, *args, **kwargs):
        lot = request.query_params.get('lot')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        query = self.model.objects.filter(Q(lot__datetime_arrival__year=year) & Q(lot__datetime_arrival__month=month))
        if lot:
            query = query.filter(lot__lot__icontains=lot)
        serializer = self.serializer_class(query, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class FreightDetailAPIView(APIView):
    model = Freight
    serializer_class = FreightSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Flete actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class GLPListAPIView(APIView):
    model = GLP
    serializer_class = GLPSerializer

    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        if not all([month, year]):
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        query = self.model.objects.filter(Q(date__year=year) & Q(date__month=month))
        serializer = self.serializer_class(query, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class GLPDetailAPIView(APIView):
    model = GLP
    serializer_class = GLPSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Registro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Flete actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class DownloadLotUpdateAPIView(APIView):
    model = DownloadLot
    serializer_class = DownloadLotSerializer

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
        try:
            item.delete()
            return Response({'message': 'Registro eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el registro porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PalletListAPIView(APIView):
    model = Pallets
    serializer_class = PalletsSerializer

    def get(self, request, *args, **kwargs):
        items = self.model.objects.all()
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class ItemsLotListAPIView(APIView):
    model = ItemsLot
    serializer_class = ItemsLotSerializer

    def get(self, request, *args, **kwargs):
        lot = request.query_params.get('lot')
        if lot:
            items = self.model.objects.filter(lot__lot__icontains=lot)
            serializer = self.serializer_class(items, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'data': []}, status=status.HTTP_404_NOT_FOUND)

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Item creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemsLotUpdateAPIView(APIView):
    model = ItemsLot
    serializer_class = ItemsLotSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Item no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Item actualizado exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Item no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Item eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el item porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el item: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StockAvailableListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        query = Lot.objects.filter(Q(stock__gt=0) | Q(stock__lt=0))
        data = [{"id": lot.id, "lot": lot.lot, "product": lot.product.name, "stock": lot.stock} for lot in query]
        return Response({'data': data}, status=status.HTTP_200_OK)


class OutputListAPIView(APIView):
    model = Output
    serializer_class = OutputSerializer

    def get(self, request, *args, **kwargs):
        lot = request.query_params.get('lot')
        date = request.query_params.get('date')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        query = self.model.objects.all()
        if lot:
            query = query.filter(lot__lot__icontains=lot)
        if date:
            query = query.filter(date=date)
        else:
            if year:
                query = query.filter(date__year=year)
            if month:
                query = query.filter(date__month=month)
            else:
                query = query.order_by('-date')[0:50]
        serializer = self.serializer_class(query, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Salida creada exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class OutputDetailAPIView(APIView):
    model = Output
    serializer_class = OutputSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Salida no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Salida actualizada exitosamente.'}, status=status.HTTP_200_OK)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Salida no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Salida eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar el item porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el item: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MaterialListAPIView(APIView):
    model = Material
    serializer_class = MaterialSerializer

    def calculate_lead_time(self, last_receipt):
        date_order = last_receipt.po_date
        date_receipt = last_receipt.arrival_date
        return (date_receipt - date_order).days

    def calculate_consumption(self, item, year_ago, lead_time, manufacturer):
        issues = ItemsIssue.objects.filter(item__item=item, date__gte=year_ago, manufacturing=manufacturer)
        count_issues = issues.count()
        consumption_issues = issues.aggregate(Sum('quantity'))['quantity__sum'] or 0
        consumption_day = consumption_issues / count_issues if count_issues > 0 else 0

        lead_time_max = lead_time + 5
        lead_time_avg = round((lead_time_max + lead_time) / 2, 0)

        lead_time_request = round(lead_time_avg * consumption_day, 2) if lead_time_avg > 0 else 0
        safety_stock = round((lead_time_max - lead_time_avg) * consumption_day,
                             2) if lead_time_max > lead_time_avg else 0
        reorder_point = lead_time_request + safety_stock

        return {"lead_time_request": lead_time_request, "lead_time_avg": lead_time_avg, "safety_stock": safety_stock,
                "reorder_point": reorder_point, "consumption_day": consumption_day}

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name', '')
        group = request.query_params.get('group')
        manufacturer = request.query_params.get('manufacturer')

        if not all([group, manufacturer]):
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)
        items = Material.objects.filter(group__name__icontains=group)
        if name:
            items = items.filter(name__icontains=name)
        items = items.prefetch_related('itemsreceipt_set', 'group')  # Mejora el rendimiento en el acceso a relaciones
        response_data = []
        year_ago = timezone.now() - timedelta(days=365)
        for item in items:
            receipts = item.itemsreceipt_set.filter(manufacturing=manufacturer)
            incoming = receipts.filter(stock__gt=0)
            stock = receipts.aggregate(total_stock=Sum('stock'))['total_stock'] or 0

            total_value = \
                incoming.annotate(value=F('price_per_unit') * F('quantity')).aggregate(total_value=Sum('value'))[
                    'total_value'] or 0
            weighted_avg_price = total_value / stock if stock > 0 else 0

            last_receipt = receipts.order_by('-arrival_date').first()

            if last_receipt:
                lead_time = self.calculate_lead_time(last_receipt)
                consumption_info = self.calculate_consumption(item, year_ago, lead_time, manufacturer)
                info = {"id": item.id, "name": item.name, "group": item.group.id,
                        "unit_of_measurement": item.unit_of_measurement, "sap_code": item.sap,
                        "lead_time_avg": consumption_info['lead_time_avg'],
                        "safety_stock": consumption_info['safety_stock'],
                        "consumption_day": consumption_info['consumption_day'],
                        "reorder_point": consumption_info['reorder_point'], "stock": stock,
                        "weighted_avg_price": weighted_avg_price}
            else:
                info = {"id": item.id, "name": item.name, "group": item.group.id,
                        "unit_of_measurement": item.unit_of_measurement, "sap_code": item.sap, "stock": stock,
                        "weighted_avg_price": weighted_avg_price}

            response_data.append(info)

        return Response({'data': response_data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Artículo creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemsReceiptListAPIView(APIView):
    model = ItemsReceipt
    serializer_class = ItemsReceiptSerializer

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        group = request.query_params.get('group')
        manufacturer = request.query_params.get('manufacturer')
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not all([group, manufacturer, year, month]):
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        if name:
            items = self.model.objects.filter(item__name__icontains=name, item__group__name__icontains=group,
                                              manufacturing=manufacturer, arrival_date__year=year,
                                              arrival_date__month=month)
            serializer = self.serializer_class(items, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        items = self.model.objects.filter(manufacturing=manufacturer, arrival_date__year=year,
                                          arrival_date__month=month, item__group__name__icontains=group)
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Ingreso creado exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemsReceiptDetailAPIView(APIView):
    model = ItemsReceipt
    serializer_class = ItemsReceiptSerializer

    def get(self, request, pk, *args, **kwargs):
        manufacturing = request.query_params.get('manufacturing')
        if not manufacturing:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = Material.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Artículo no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        incomes = self.model.objects.filter(Q(item=item) & Q(manufacturing=manufacturing)).exists()
        if incomes:
            items = self.model.objects.filter(Q(item=item) & Q(stock__gt=0) & Q(manufacturing=manufacturing))
            data = [{"id": item.id, "name": f'{item.item.name} - {item.stock} {item.item.unit_of_measurement}',
                     "stock": item.stock} for item in items]
            return Response({'data': data}, status=status.HTTP_200_OK)
        else:
            return Response({'data': []}, status=status.HTTP_404_NOT_FOUND)


class ItemsIssueListAPIView(APIView):
    model = ItemsIssue
    serializer_class = ItemsIssueSerializer

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        group = request.query_params.get('group')
        manufacturer = request.query_params.get('manufacturer')
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not all([group, manufacturer, year, month]):
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        if name:
            items = self.model.objects.filter(item__item__name__icontains=name,
                                              item__item__group__name__icontains=group, manufacturing=manufacturer,
                                              date__year=year, date__month=month)
            serializer = self.serializer_class(items, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        items = self.model.objects.filter(manufacturing=manufacturer, date__year=year, date__month=month,
                                          item__item__group__name__icontains=group)
        serializer = self.serializer_class(items, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Salida creada exitosamente.'}, status=status.HTTP_201_CREATED)
        errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
        return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class TransferWarehouseAPIView(APIView):
    model = ItemsReceipt

    def post(self, request, *args, **kwargs):
        item_id = request.data.get('item')
        manufacturing = request.data.get('manufacturing')
        quantity = request.data.get('quantity')

        if not all([item_id, manufacturing, quantity]):
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("La cantidad debe ser mayor a cero.")
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                article = self.model.objects.get(pk=item_id)
                if article.manufacturing == manufacturing:
                    return Response({'error': 'No se puede transferir al mismo almacén.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                if article.stock < quantity:
                    return Response({'error': 'Stock insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

                transfer = self.model.objects.filter(item=article.item, po_number=article.po_number,
                                                     po_date=article.po_date, arrival_date=article.arrival_date,
                                                     supplier=article.supplier, invoice=article.invoice,
                                                     manufacturing=manufacturing,
                                                     price_per_unit=article.price_per_unit, )

                if transfer.exists():
                    transfer = transfer.first()
                    transfer.quantity += quantity
                    transfer.save()
                    transfer.calc_stock()
                else:
                    new=self.model.objects.create(item=article.item, po_number=article.po_number, po_date=article.po_date,
                                              arrival_date=article.arrival_date, supplier=article.supplier,
                                              invoice=article.invoice, manufacturing_id=manufacturing,
                                              price_per_unit=article.price_per_unit, quantity=quantity,stock=quantity)
                    new.calc_stock()
                article.quantity -= quantity
                article.save()
                article.calc_stock()

                return Response({'message': 'Transferencia realizada exitosamente.'}, status=status.HTTP_201_CREATED)
        except ItemsReceipt.DoesNotExist:
            return Response({'error': 'Artículo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Error en el servidor. Intente de nuevo más tarde.'
                                      'detail: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotifyTwilioOrderView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        quantity = request.data.get('quantity')
        location = request.data.get('location')

        if not all([name, quantity, location]):
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        account_sid = 'ACe40758ca26ec30239cd9116763c7c0c7'
        auth_token = '0ae02c9b83a48a9fcdb31dfd8adc35ad'
        client = Client(account_sid, auth_token)

        message = client.messages.create(from_='whatsapp:+14155238886',
                                         body=f'¡Hola! Se ha solicitado {quantity} unidades de {name} para el almacén {location}.',
                                         to='whatsapp:+51982704759')
        return Response({'message': 'Mensaje enviado exitosamente.'}, status=status.HTTP_200_OK)


class MaterialMaintenanceListAPIView(APIView):
    model = Material
    serializer_class = MaterialSerializer

    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name', '')

        items = Material.objects.all()
        if name:
            items = items.filter(name__icontains=name)

        items = items.prefetch_related('itemsreceipt_set', 'group')
        response_data = []

        for item in items:
            receipts = item.itemsreceipt_set.filter(Q(manufacturing__ruc='20568075278') & Q(stock__gt=0))
            stock = receipts.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
            total_value = \
                receipts.annotate(value=F('price_per_unit') * F('quantity')).aggregate(total_value=Sum('value'))[
                    'total_value'] or 0
            weighted_avg_price = total_value / stock if stock > 0 else 0

            response_data.append({'id': item.id, 'name': item.name, 'group': item.group.id,
                                  'unit_of_measurement': item.unit_of_measurement, 'sap_code': item.sap, 'stock': stock,
                                  'weighted_avg_price': weighted_avg_price})
        return Response({'data': response_data}, status=status.HTTP_200_OK)


class DocumentListView(APIView):
    model = Files
    serializer_class = FilesSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Documento añadido exitosamente'}, status=status.HTTP_201_CREATED)
        else:
            errors = '; '.join(['{}: {}'.format(key, ' '.join(value)) for key, value in serializer.errors.items()])
            return Response({'error': 'Error de validación: ' + errors}, status=status.HTTP_400_BAD_REQUEST)


class DocumentDetailView(APIView):
    model = Files
    serializer_class = FilesSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.filter(lot__lot=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Documento no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        try:
            item = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({'error': 'Documento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            item.delete()
            return Response({'message': 'Documento eliminado exitosamente.'}, status=status.HTTP_200_OK)
        except ProtectedError:
            return Response({'error': 'No se puede eliminar  porque tiene registros relacionados.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error al eliminar el registro: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LotListView(APIView):
    model = Lot
    serializer_class = LotSerializer

    def get(self, request):
        lot = request.query_params.get('lot')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        week = request.query_params.get('week')
        product = request.query_params.get('type')
        if not product and year:
            return Response({'error': 'Faltan datos requeridos en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.model.objects.filter(
            Q(product__name__icontains=product) & Q(datetime_download_started__year=year))

        if lot:
            queryset = queryset.filter(lot__icontains=lot)
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(datetime_download_started__month=month)
        else:
            if week and week.isdigit() and 1 <= int(week) <= 52:
                queryset = queryset.filter(datetime_download_started__week=week)
            else:
                queryset = queryset.order_by('-datetime_download_started')[0:50]
        serializer = self.serializer_class(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
