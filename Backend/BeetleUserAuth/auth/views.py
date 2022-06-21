import base64
from http import HTTPStatus

from .serializers import UserSerializer
from .serializers import RegisterSerializer
from .utils import generate_pass

from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.contrib.auth import authenticate
from django.core.mail import send_mail

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_pass_api(request):
    json_data=JSONParser().parse(request)
    req_auth_info = request.headers.get('Authorization')
    auth_info=base64.b64decode(req_auth_info[6:]).decode()
    auth_info=auth_info.split(":")
    user = User.objects.get(username=auth_info[0])
    user.set_password(json_data["update"])
    user.save()
    return JsonResponse("Password reset successfull",safe=False, status=HTTPStatus.OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def recover_api(request):
    email = JSONParser().parse(request)["email"]
    
    if(User.objects.filter(username=email).exists()):
        new_password = generate_pass()
        user = User.objects.filter(username=email).get()
        user.set_password(new_password)
        user.save()
        send_mail('Password Reset', 'Your new password is: ' + new_password , None,
                  recipient_list=[email],
                  fail_silently=False,)
        return JsonResponse("Password reset successfull",safe=False, status=HTTPStatus.OK)
    else:
        return JsonResponse("Invalid Email",safe=False, status=HTTPStatus.FORBIDDEN)
    
@api_view(['POST'])
def login_api(request):
    req_auth_info = request.headers.get('Authorization')
    if not req_auth_info:
        return JsonResponse("Auth info not provided",safe=False, status=HTTPStatus.BAD_REQUEST)
    auth_info=base64.b64decode(req_auth_info[6:]).decode()
    auth_info=auth_info.split(":")
    user = authenticate(username=auth_info[0], password=auth_info[1])
    if user is not None:
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data,safe=False)    
    else:
        return JsonResponse("Invalid Username or Password",safe=False, status=HTTPStatus.FORBIDDEN)
