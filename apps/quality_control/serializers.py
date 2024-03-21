from rest_framework import serializers

from .models import (AnalysisPineapple, AnalysisSweetPotato)


class AnalysisPineappleSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)

    class Meta:
        model = AnalysisPineapple
        fields = '__all__'


class AnalysisSweetPotatoSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source='lot.lot', read_only=True)

    class Meta:
        model = AnalysisSweetPotato
        fields = '__all__'
