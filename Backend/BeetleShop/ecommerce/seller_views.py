from django.http.response import JsonResponse

from ecommerce.models import Store, Category, Item, Order
from ecommerce.serializers import StoreSerializer, CategorySerializer, ItemSerializer, OrderSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status

@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def seller_stores_api(request, owner_id):
    if request.method == "GET":
        stores = Store.objects(owner_id = owner_id).all()
        if(not stores):
            return JsonResponse({"message" : "No store found"}, status=status.HTTP_404_NOT_FOUND)
            
        store_serializer = StoreSerializer(stores, many=True)
        return JsonResponse(store_serializer.data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_orders_api(request, store_id):
    if request.method=="GET":
        orders = Order.objects(store=store_id).all()

        if not orders:
            return JsonResponse({'message' : 'No orders found'}, status=status.HTTP_404_NOT_FOUND)

        order_serializer = OrderSerializer(orders , many=True)
        return JsonResponse(order_serializer.data ,safe=False, status=status.HTTP_200_OK)