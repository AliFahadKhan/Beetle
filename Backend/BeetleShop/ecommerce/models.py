from datetime import datetime
from mongoengine import Document, connect, LongField, StringField, FileField, ListField, ObjectIdField, DateTimeField, DictField, BooleanField


connect( db="ecomm-db", username="Beetle", password="cBctbaMZIcarfP33", host="mongodb+srv://Beetle:cBctbaMZIcarfP33@cluster0.ajmpj.mongodb.net/ecomm_db?retryWrites=true&w=majority")

class Store(Document):
    owner_id = LongField(default=0, required=True)
    owner_name = StringField(default="", required =True)
    name = StringField(default="", required=True)
    location = StringField(default="", required=True)
    image = FileField()

class Category(Document):
    name = StringField(default="", required=True)

class Item(Document):
    store = ObjectIdField(required=True)
    category = StringField(required=True)
    name = StringField(default="", required=True)
    image = FileField()
    description = StringField(default="", required=True)
    price = LongField(default=0, required=True)
    quantity = LongField(default=0, required=True)
    crops = ListField(StringField(max_length=50))
    chemicals = ListField(StringField(max_length=50))
    diseases = ListField(StringField(max_length=50))
    credit_available = BooleanField(default=False)
    in_stock = BooleanField(default=True)

class Order(Document):
    buyer_id = LongField(default=0, required=True)
    delivery_address = StringField(default="", required=True)
    store = ObjectIdField(required=True)
    amount = LongField(default=0)
    items = ListField(DictField())
    date_created = DateTimeField(default=datetime.utcnow)
    accepted = BooleanField(default=False)
    on_credit = BooleanField(default=False)
