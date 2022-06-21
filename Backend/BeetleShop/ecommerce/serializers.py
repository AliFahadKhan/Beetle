from rest_framework_mongoengine.serializers import DocumentSerializer
from ecommerce.models import Store, Category, Item, Order

class StoreSerializer(DocumentSerializer):
    class Meta:
        model = Store
        depth = 2

class CategorySerializer(DocumentSerializer):
    class Meta:
        model = Category
        depth = 2

class ItemSerializer(DocumentSerializer):
    class Meta:
        model = Item
        fields = ('id', 'store', 'category', 'name', 'image', 'description', 'price', 'quantity', 'crops', 
                  'chemicals', 'diseases', 'credit_available')

class OrderSerializer(DocumentSerializer):
    class Meta:
        model = Order
        fields = ('id', 'buyer_id', 'store', 'amount', 'items', 'date_created', 'delivery_address')
        depth = 2