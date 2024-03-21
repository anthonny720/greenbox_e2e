from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Departments, Position
from .serializers import DepartmentSerializer, PositionSerializer


# Create your views here.

class DepartmentsListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        departments = Departments.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class PositionListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        positions = Position.objects.all()
        serializer = PositionSerializer(positions, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
