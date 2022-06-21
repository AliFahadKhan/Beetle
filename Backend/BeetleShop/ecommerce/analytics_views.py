from django.http.response import JsonResponse

from ecommerce.models import Item
from ecommerce.serializers import ItemSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from rest_framework import status


@api_view(['POST'])
@permission_classes([AllowAny])
def product_recommend_api(request):
    disease_info = JSONParser().parse(request)

    items = Item.objects(name__in = disease_info["products"]).all()
    if items:
        item_serializer = ItemSerializer(items, many=True)
        return JsonResponse(item_serializer.data, status=status.HTTP_200_OK, safe=False)
    
    return JsonResponse({"Message" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)