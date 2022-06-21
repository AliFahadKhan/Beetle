from django.urls import path
from auth.views import RegisterView
from auth import views


urlpatterns = [
    path('login/', views.login_api),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('recover/', views.recover_api),
    path('update/pass', views.update_pass_api),
]