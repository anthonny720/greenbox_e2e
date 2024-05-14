from apps.logistic.serializers import MaterialSerializer
from apps.user.serializers import HelperSerializer
from rest_framework import serializers

from .models import (FixedAsset, PhysicalAsset, Tool, Failure, Type, Requirements, ResourceItem, HelperItem,
                     WorkOrder, H2O, Chlorine, )


class FixedAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedAsset
        fields = '__all__'


class ToolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = '__all__'


class PhysicalAssetSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = PhysicalAsset
        fields = '__all__'


class FailureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Failure
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class RequirementsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Requirements
        fields = '__all__'


class ResourceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResourceItem
        fields = '__all__'


class HelperItemSerializer(serializers.ModelSerializer):
    helper = HelperSerializer()
    time = serializers.CharField(source='get_time', read_only=True)

    class Meta:
        model = HelperItem
        fields = '__all__'


class WorkOrderSerializer(serializers.ModelSerializer):
    code_ot = serializers.CharField(source='code', read_only=True)
    time = serializers.CharField(source='get_time', read_only=True)
    facility = serializers.CharField(source='asset.parent.name', read_only=True)

    class Meta:
        model = WorkOrder
        fields = '__all__'

class H2OSerializer(serializers.ModelSerializer):
    class Meta:
        model = H2O
        fields = '__all__'



class ChlorineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chlorine
        fields = '__all__'