from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializers import UserRegisterSerializer,UserDetailSerializer,EmailSerializer
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


class UserDetailView(RetrieveAPIView):
    """用户信息展示视图"""

    serializer_class = UserDetailSerializer
    #用户身份设置：是否是登陆用户
    permission_classes = [IsAuthenticated]

    # 重写get_object方法，返回用户详情模型对象
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """更新邮箱"""

    serializer_class = EmailSerializer

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    """激活用户邮箱"""

    def get(self, request):
        # 获取前端查询字符串中传入的token
        token = request.query_params.get('token')
        # 把token解密 并查询对应的user
        user = User.check_verify_email_token(token)
        # 修改当前user的email_active为True
        if user is None:
            return Response({'message': '激活失败'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        # 响应
        return Response({'message': 'ok'})


