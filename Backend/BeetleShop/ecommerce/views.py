import base64

from django.http.response import JsonResponse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

from mongoengine.connection import get_db

from ecommerce.models import Store, Category, Item, Order
from ecommerce.serializers import StoreSerializer, CategorySerializer, ItemSerializer, OrderSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status

from bson import ObjectId
import gridfs

db= get_db()
fs = gridfs.GridFS(db)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def image_api(request, file_id):
    oid = ObjectId(file_id)
    img=base64.b64encode(fs.get(oid).read()).decode('utf-8')
    return JsonResponse({"image_id": file_id, "image": img})

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def stores_api(request):
    if request.method=="POST":
        store_data=JSONParser().parse(request)

        req_auth_info = request.headers.get('Authorization')
        auth_info=base64.b64decode(req_auth_info[6:]).decode()
        auth_info=auth_info.split(":")
        req_user = User.objects.get(username=auth_info[0])
        store_data["owner_id"] = req_user.pk
        store_data["owner_name"] = req_user.first_name + " " + req_user.last_name

        if "image" in store_data.keys():
            decode = base64.b64decode(store_data["image"])
            file = ContentFile(decode, name="image.png")
            store_data["image"] = file
        store_serializer = StoreSerializer(data=store_data)
        if store_serializer.is_valid():
            store_serializer.save()
            return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(store_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=="GET":
        search = request.GET.get("search","")
        if search != "":
            stores = Store.objects(name__contains=search)

        else:
            stores = Store.objects.all()
        
        if(not stores):
            return JsonResponse({"message" : "No store found"}, status=status.HTTP_404_NOT_FOUND)
            
        store_serializer = StoreSerializer(stores, many=True)
        return JsonResponse(store_serializer.data, safe=False)

@api_view(["GET", "PUT" ,"DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def store_api(request, store_id):
    try:
        store = Store.objects(id=store_id).get()
    except:
        return JsonResponse({"Message": "The Store does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        store_serializer = StoreSerializer(store)
        store_items = Item.objects(store=store_id)
        if store_items:
            item_serializer = ItemSerializer(store_items, many=True)
            store_data = store_serializer.data.copy()
            store_data["items"] = item_serializer.data
        return JsonResponse(store_data, status=status.HTTP_200_OK)
    
    req_auth_info = request.headers.get('Authorization')
    auth_info=base64.b64decode(req_auth_info[6:]).decode()
    auth_info=auth_info.split(":")
    req_user = User.objects.get(username=auth_info[0])

    if (store.owner_id != req_user.pk):
        return JsonResponse({"Message" : "Unauthorized Operation"}, status=status.HTTP_403_FORBIDDEN, safe=False)

    elif request.method == "DELETE":
        Item.objects(store=store["id"]).delete()
        store.delete()
        return JsonResponse({"Message" : "Store deleted successfully"}, status=status.HTTP_200_OK, safe=False)
    
    elif request.method == "PUT":
        store_data=JSONParser().parse(request)
        if "image" in store_data.keys():
            decode = base64.b64decode(store_data["image"])
            file = ContentFile(decode, name="image.png")
            store_data["image"] = file
        store_serializer = StoreSerializer(data=store_data)
        if store_serializer.is_valid():
            if "image" in store_serializer.validated_data.keys():
                curr_image_id = store["image"]
                new_image = store_serializer.validated_data.get("image")
                store_serializer.validated_data.pop("image")
                store["image"] = new_image
                store.save()
                if curr_image_id:
                    fs.delete(ObjectId(curr_image_id.grid_id))
            Store.objects(id=store_id).update_one(**store_serializer.validated_data)
            return JsonResponse({"Message" : "Updated Successfully"}, safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(store_serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def categories_api(request):
    if request.method=="POST":
        category_data=JSONParser().parse(request)
        category_serializer = CategorySerializer(data=category_data)
        if category_serializer.is_valid():
            category_serializer.save()
            return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(category_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=="GET":
        search = request.GET.get('search','')
        if search != '':
            categories = Category.objects(name__contains=search)
        else:
            categories = Category.objects.all()
        if(not categories):
            return JsonResponse({'message' : 'No category found'}, status=status.HTTP_404_NOT_FOUND)
        category_serializer = CategorySerializer(categories, many=True)
        return JsonResponse(category_serializer.data, safe=False)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def items_api(request):
    if request.method=="POST":
        item_data=JSONParser().parse(request)

        if "image" in item_data.keys():
            decode = base64.b64decode(item_data["image"])
            file = ContentFile(decode, name="image.png")
            item_data["image"] = file

        item_serializer = ItemSerializer(data=item_data)
        if item_serializer.is_valid():
            item_serializer.save()
            return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(item_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=="GET":
        search_query = request.GET.get('search','')
        category_query = request.GET.get('category','')
        sort_query = request.GET.get('sort','')
        order_query = request.GET.get('order','')
        if search_query != '':
            items = Item.objects(name__icontains=search_query).filter(in_stock=True)
        elif category_query != '':
            items = Item.objects(category=category_query).filter(in_stock=True)
        else:
            items = Item.objects().filter(in_stock=True)
        
        if sort_query and order_query:
            if order_query == 'asc':
                items=items.order_by('+'+sort_query)
            elif order_query == 'desc':
                items=items.order_by("-"+sort_query)

        if(not items):
            return JsonResponse({'message' : 'No Item found'}, status=status.HTTP_404_NOT_FOUND)
        item_serializer = ItemSerializer(items, many=True)
        return JsonResponse(item_serializer.data, safe=False)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def item_api(request, item_id):
    try:
        item = Item.objects(id=item_id).exclude("in_stock").get()
    except:
        return JsonResponse({"Message": "The Item does not exist"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        item_serializer = ItemSerializer(item)
        return JsonResponse(item_serializer.data, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        item.delete()
        return JsonResponse({"Message" : "Item deleted successfully"}, status=status.HTTP_200_OK, safe=False)
    elif request.method == "PUT":
        item_data=JSONParser().parse(request)
        if "image" in item_data.keys():
            decode = base64.b64decode(item_data["image"])
            file = ContentFile(decode, name="image.png")
            item_data["image"] = file
        item_serializer = ItemSerializer(data=item_data)
        if item_serializer.is_valid():
            if "image" in item_serializer.validated_data.keys():
                curr_image_id = item["image"]
                new_image = item_serializer.validated_data.get("image")
                item_serializer.validated_data.pop("image")
                item["image"] = new_image
                item.save()
                if curr_image_id:
                    fs.delete(ObjectId(curr_image_id.grid_id))
            Item.objects(id=item_id).update_one(**item_serializer.validated_data)
            return JsonResponse({"Message" : "Updated Successfully"}, safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(item_serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_orders_api(request):

    req_auth_info = request.headers.get('Authorization')
    auth_info=base64.b64decode(req_auth_info[6:]).decode()
    auth_info=auth_info.split(":")
    req_user = User.objects.get(username=auth_info[0])

    if request.method=="POST":
        order_data=JSONParser().parse(request)
        
        items = {}
        amounts = {}
        for item in order_data["items"]:
            store = item["store"]
            if store in items.keys():
                items[store].append(item)
                amounts[store] = amounts[store] + (item["price"] * item["quantity"])
            else:
                items[store]=[item]
                amounts[store] = item["price"] * item["quantity"]
        
        orders = []
        for key, value in items.items():
            temp_order = {"amount" : 0}
            temp_order["amount"] = amounts[key]
            temp_order["delivery_address"] = order_data["delivery_address"]
            temp_order["store"] = key
            temp_order["items"] = value
            temp_order["buyer_id"] = req_user.pk

            order_serializer = OrderSerializer(data=temp_order)

            if order_serializer.is_valid():
                orders.append(Order(**order_serializer.validated_data))
            else:
                return JsonResponse(order_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)
        
        Order.objects().insert(orders)
        return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED)
    
    elif request.method=="GET":
        orders = Order.objects(buyer_id=req_user.pk).exclude("accepted").all()

        if not orders:
            return JsonResponse({'message' : 'No orders found'}, status=status.HTTP_404_NOT_FOUND)

        order_serializer = OrderSerializer(orders , many=True)
        return JsonResponse(order_serializer.data ,safe=False, status=status.HTTP_200_OK)
