from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category


# Create your views here.

class CategoryList(APIView):
    def get(self, request, *args, **kwargs):
        if Category.objects.all().exists():
            query = Category.objects.all()

            result = []
            for category in query:
                if not category.parent:
                    item = {}
                    item['id'] = category.id
                    item['name'] = category.name
                    item['children'] = []
                    for cat in query:
                        sub_item = {}
                        if cat.parent and cat.parent.id == category.id:
                            sub_item['id'] = cat.id
                            sub_item['name'] = cat.name
                            sub_item['children'] = []

                            item['children'].append(sub_item)
                    result.append(item)
            return Response({'data': result}, status=status.HTTP_200_OK)
        else:
            return Response({'data': 'No hay categorías'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
