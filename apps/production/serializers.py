from rest_framework import serializers

from .models import (ConditioningSweetPotato, ConditioningPineapple, ThumbnailProcess, Cuts, PackingLot)


class CutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuts
        fields = '__all__'


class ConditioningSweetPotatoSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)

    class Meta:
        model = ConditioningSweetPotato
        fields = '__all__'


class ConditioningPineappleSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)

    class Meta:
        model = ConditioningPineapple
        fields = '__all__'


class ThumbnailProcessSerializer(serializers.ModelSerializer):
    path = serializers.CharField(source='get_absolute_url', read_only=True)
    class Meta:
        model = ThumbnailProcess
        fields = '__all__'


class PackingLotSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)
    class Meta:
        model = PackingLot
        fields = '__all__'
