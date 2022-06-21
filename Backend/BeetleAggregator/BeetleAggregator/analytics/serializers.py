from rest_framework_mongoengine.serializers import DocumentSerializer
from analytics.models import Crop, Disease

class CropSerializer(DocumentSerializer):
    class Meta:
        model = Crop

class DiseaseSerializer(DocumentSerializer):
    class Meta:
        model = Disease
        depth = 2