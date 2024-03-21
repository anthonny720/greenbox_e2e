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

    class Meta:
        model = HelperItem
        fields = '__all__'


class WorkOrderSerializer(serializers.ModelSerializer):
    code_ot = serializers.CharField(source='code', read_only=True)
    time = serializers.CharField(source='get_time', read_only=True)
    cost = serializers.CharField(source='get_cost', read_only=True, )
    facility = serializers.CharField(source='asset.parent.name', read_only=True)
    personnel = serializers.ListField(source='get_personnel', read_only=True)
    resources_used = serializers.ListField(source='get_resources', read_only=True)
    helpers = HelperItemSerializer(many=True, read_only=True, source='helpers_order')
    signature = serializers.CharField(source='get_signature_boss', read_only=True)
    signature_supervisor = serializers.CharField(source='get_signature_supervisor', read_only=True)
    signature_requester = serializers.CharField(source='get_signature_requester', read_only=True)
    signature_planner = serializers.CharField(source='get_signature_planner', read_only=True)
    planner_name = serializers.CharField(source='get_planner_name', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.first_name', read_only=True)
    requester_name = serializers.CharField(source='requester.first_name', read_only=True)
    physical_name = serializers.CharField(source='asset.name', read_only=True)
    type_name = serializers.CharField(source='type_maintenance.name', read_only=True)
    failure_name = serializers.CharField(source='failure.name', read_only=True)
    criticality = serializers.CharField(source='asset.criticality', read_only=True)
    technical_name = serializers.CharField(source='technical.get_full_name', read_only=True)

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