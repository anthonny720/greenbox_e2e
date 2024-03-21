from rest_framework import serializers

from .models import Parcel


class ParcelSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    class Meta:
        model = Parcel
        fields = '__all__'