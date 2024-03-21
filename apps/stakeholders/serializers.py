from rest_framework import serializers

from .models import (RawMaterialSupplier, MaterialSupplier, Client, TransportationCompany,
                                              ManufacturingCompany)

class RawMaterialSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterialSupplier
        fields = '__all__'


class MaterialSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialSupplier
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class TransportationCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportationCompany
        fields = '__all__'


class ManufacturingCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturingCompany
        fields = '__all__'
