from mongoengine import Document, connect, StringField, ListField


connect( db="disease-db", username="Beetle", password="cBctbaMZIcarfP33", host="mongodb+srv://Beetle:cBctbaMZIcarfP33@cluster0.ajmpj.mongodb.net/disease_db?retryWrites=true&w=majority")

class Crop(Document):
    crop_name = StringField(default="", required =True)
    crop_description = StringField()
    crop_care = StringField()
    crop_soil = StringField()
    crop_climate = StringField()
    crop_diseases = ListField(StringField())

class Disease(Document):
    disease = StringField(default="", required=True)
    control_products = ListField(StringField())
    disease_name = StringField(default="", required =True)
    pest_name = StringField(max_length=50)
    pest_scientific_name = StringField(max_length=50)
    crops = ListField(StringField(max_length=50))
    symptoms = ListField(StringField())
    prevention = ListField(StringField())
    control_chemicals = ListField(StringField())
    control_organic = StringField()