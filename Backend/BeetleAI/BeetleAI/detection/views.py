import base64
import os
import io
from PIL import Image

from BeetleAI.settings import BASE_DIR, PROJECT_ROOT

from django.http.response import JsonResponse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.parsers import JSONParser
from rest_framework import status

from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
import tensorflow as tf

tf.compat.v1.disable_eager_execution()

@api_view(['POST'])
def detection_api(request):
    crop_data=JSONParser().parse(request)
    CLASSIFIER_FOLDER = os.path.join(BASE_DIR, 'models/')

    if crop_data["crop"] == "pepper":
        label_encoding = {0 : "Pepper Bacterial Spot", 1 : "Healthy"}  
        model_file = os.path.join(CLASSIFIER_FOLDER, "pepper_model.hdf5")
        print(model_file)
        model = load_model(model_file)
    
    elif crop_data["crop"] == "potato":
        label_encoding = {0: 'Potato Early Blight', 1: 'Healthy', 2: 'Potato Late Blight'}
        model_file = os.path.join(CLASSIFIER_FOLDER, "potato_model.hdf5")
        print(model_file)
        model = load_model(model_file)
    
    elif crop_data["crop"] == "citrus":
        label_encoding={0:'Citrus Black Spot', 1:'Citrus Canker', 2:'Citrus Greening Disease', 3: 'Healthy'}
        model_file = os.path.join(CLASSIFIER_FOLDER, "citrus_model.hdf5")
        print(model_file)
        model = load_model(model_file)
    
    elif crop_data["crop"] == "tomato":
        label_encoding={0:'Tomato Bacterial Spot', 
                        1:'Tomato Early Blight', 
                        2:'Tomato Late Blight', 
                        3:'Tomato Leaf Mold', 
                        4:'Tomato Septoria Leaf Spot', 
                        5:'Tomato Spider Mites', 
                        6:'Tomato Target Spot', 
                        7:'Tomato Yellow Leaf Curl Virus', 
                        8:'Tomato Mosaic Virus', 
                        9:'Healthy'}
        model_file = os.path.join(CLASSIFIER_FOLDER, "tomato_model.hdf5")
        print(model_file)
        model = load_model(model_file)
    
    decode = base64.b64decode(crop_data["image"])
    image = Image.open(io.BytesIO(decode))
    image = image.resize((224,224))
    image = image.convert("RGB")
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)

    yhat = model.predict(image)
    label = yhat.argmax(axis=1)[0]
    output = {"prediction" : label_encoding[label], "percentage" : yhat[0][label]*100}

    return JsonResponse(output,safe=False, status=status.HTTP_200_OK)
