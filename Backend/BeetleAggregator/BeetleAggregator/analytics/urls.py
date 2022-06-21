from django.urls import path
from analytics import views 
 
urlpatterns = [
    path('analyse', views.detect_api),

    path('crops', views.crops_api),
    path('addCrop', views.add_crop_api),
    path('diseases', views.diseases_api),
    path('addDisease', views.add_disease_api)
    
]
