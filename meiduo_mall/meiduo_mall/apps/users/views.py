from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserRegisterSerializer
from .models import User


class UserRegisterView(CreateAPIView):
    """注册序列化器"""

    serializer_class = UserRegisterSerializer


class UsernameCountView(APIView):
    """判断用户名是否已经注册"""

    def get(self,request,username):

        count = User.objects.filter(username=username).count()

        data = {
            "username":username,
            "count":count
        }

        return Response(data=data)

class UserMobileView(APIView):
    """判断手机号码是否已经注册视图"""

    def get(self,request,mobile):

        count = User.objects.filter(mobile=mobile).count()

        data = {
            "mobile":mobile,
            "count":count
        }

        return Response(data=data)


