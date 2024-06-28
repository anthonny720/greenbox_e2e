from rest_framework import serializers

from .models import (ExternalPeople, Lot, DownloadLot, Pallets, ItemsLot, Output, Material, ItemsIssue, ItemsReceipt,
                     Freight, GLP, Files)


class ExternalPeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalPeople
        fields = '__all__'


class LotSummarySerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = Lot
        fields = (
            'id', 'lot', 'product', 'datetime_download_started', 'condition', 'stock', 'weight_net', 'download_price',
            'freight', 'plant_price', 'weight_usable', 'freight_boxes', 'discount_price_kg', 'discount_price',
            'weight_reject')

class LotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = '__all__'


class DownloadLotSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)
    datetime_download = serializers.CharField(source='lot.datetime_download_started', read_only=True)
    weight_net = serializers.CharField(source='lot.weight_net', read_only=True)
    external_name = serializers.CharField(source='external.full_name', read_only=True)

    class Meta:
        model = DownloadLot
        fields = '__all__'


class FreightSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)
    date = serializers.CharField(source='lot.datetime_download_started', read_only=True)
    supplier = serializers.CharField(source='lot.transport.name', read_only=True)
    transport_guide = serializers.CharField(source='lot.transport_guide', read_only=True)

    class Meta:
        model = Freight
        fields = '__all__'


class GLPSerializer(serializers.ModelSerializer):
    class Meta:
        model = GLP
        fields = '__all__'


class PalletsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pallets
        fields = '__all__'


class ItemsLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsLot
        fields = '__all__'


class OutputSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)

    class Meta:
        model = Output
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class ItemsIssueSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item.name', read_only=True)
    oc = serializers.CharField(source='item.po_number', read_only=True)
    price = serializers.CharField(source='item.price_per_unit', read_only=True)

    class Meta:
        model = ItemsIssue
        fields = '__all__'


class ItemsReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsReceipt
        fields = '__all__'


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = '__all__'
