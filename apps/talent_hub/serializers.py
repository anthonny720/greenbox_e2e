from rest_framework import serializers

from .models import (Absenteeism, Staff, Tracking, Holiday)


class AbsenteeismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absenteeism
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)

    def get_path(self, obj):
        return obj.get_image_url()

    class Meta:
        model = Staff
        fields = (
            'id', 'name', 'last_name', 'full_name', 'dni', 'photo', 'email', 'status', 'phone', 'position', 'birthday',
            'date_of_admission', 'date_of_farewell', 'area', 'overtime_hours', 'trusted', 'hours_per_day',
            'hours_saturday', 'hours_sunday', 'area_name', 'position_name',)


class TrackingSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True)

    class Meta:
        model = Tracking
        fields = '__all__'


class TrackingSummarySerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True)
    real_time = serializers.CharField(source='get_real_worked_hours', read_only=True)

    class Meta:
        model = Tracking
        fields = ('staff_name', 'date', 'real_check_in', 'lunch_start', 'real_lunch_end', 'check_out', 'real_time')


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
