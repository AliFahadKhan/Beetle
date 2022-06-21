import requests

from django.http.response import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.parsers import JSONParser
from rest_framework import status

from analytics.models import Crop, Disease
from analytics.serializers import CropSerializer, DiseaseSerializer

import pandas as pd
from numpy import argwhere
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


AI_URL = 'http://localhost:8040/detection/detect'
ECOMM_URL = 'https://beetle-shop.azurewebsites.net/shop/items'

@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def detect_api(request):
    user_input = JSONParser().parse(request)

    response = requests.post(AI_URL, json=user_input)
    response_json = response.json()

    print(response_json)

    if response_json['prediction'] == 'Healthy':
        return JsonResponse(response_json, status=status.HTTP_200_OK)
    else:
        disease = Disease.objects(disease=response_json['prediction']).get()
        response = requests.get(ECOMM_URL)
        item_data = response.json()

        query_string = " ".join(disease["control_products"])
        query_string += " " + disease["disease"]
        query_string += " " + " ". join(disease["control_chemicals"])

        if item_data:
            items_df = pd.DataFrame.from_dict(item_data)
            items_df = items_df[["name", "diseases", "chemicals"]]
            items = suggest_items(query_string, items_df)
            print(items)
        else:
            items = []

        result_json = {}
        result_json["prediction"] = response_json["prediction"]
        result_json["percentage"] = response_json["percentage"] 
        result_json["disease_details"] = DiseaseSerializer(disease).data

        if items:
            result_json["items_found"] = True
            result_json["items"] = [item_data[item] for item in items]
        else:
            result_json["items_found"] = False
            result_json["items"] = []
            
            
        return JsonResponse(result_json, status=status.HTTP_200_OK)

def suggest_items(query_string, items_df):
    items_df["diseases"] = [' '.join(map(str, x)) for x in items_df['diseases']]
    items_df["chemicals"] = [' '.join(map(str, x)) for x in items_df['chemicals']]

    items_string_list = [" ".join(row) for row in items_df.to_numpy().tolist()]
    
    tfidf_vectorizer = TfidfVectorizer()
    sparse_matrix = tfidf_vectorizer.fit_transform(items_string_list)
    doc_term_matrix = sparse_matrix.toarray()

    query_transform = tfidf_vectorizer.transform([query_string]).toarray()
    tgt_cosine = cosine_similarity(doc_term_matrix,query_transform).flatten()
    relevant_indices = argwhere(tgt_cosine>0.7).flatten().tolist()
            
    if len(relevant_indices) >= 3:
        relevant_indices = sorted(relevant_indices, key = lambda x: tgt_cosine[x])[-3:]
        print(relevant_indices)

    return relevant_indices

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def crops_api(request):
    crops = Crop.objects.all()

    if not crops:
        return JsonResponse({"message" : "No crop found"}, status=status.HTTP_404_NOT_FOUND)
            
    crop_serializer = CropSerializer(crops, many=True)
    return JsonResponse(crop_serializer.data, safe=False)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_crop_api(request):
    if request.method=="POST":
        crop_data=JSONParser().parse(request)
        crop_serializer = CropSerializer(data=crop_data)
        if crop_serializer.is_valid():
            crop_serializer.save()
            return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(crop_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def diseases_api(request):
    diseases = Disease.objects.all()

    if not diseases:
        return JsonResponse({"message" : "No disease found"}, status=status.HTTP_404_NOT_FOUND)
            
    disease_serializer = DiseaseSerializer(diseases, many=True)
    return JsonResponse(disease_serializer.data, safe=False)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_disease_api(request):
    if request.method=="POST":
        disease_data=JSONParser().parse(request)
        disease_serializer = DiseaseSerializer(data=disease_data)
        if disease_serializer.is_valid():
            disease_serializer.save()
            return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(disease_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)
