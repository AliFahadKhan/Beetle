from django.urls import path
from detection import views 
 

urlpatterns = [ 
    path('detect',views.detection_api),
]