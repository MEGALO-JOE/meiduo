from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView,RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status,mixins
from rest_framework.viewsets import GenericViewSet
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken
from datetime import datetime

from carts.utils import merge_cart_cookie_to_redis
from goods.models import SKU
from goods.serializers import SKUSerializer
from .models import User
from . import constants
from . import serializers


class UserRegisterView(CreateAPIView):
    """注册序列化器"""

    serializer_class = serializers.UserRegisterSerializer


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

    serializer_class = serializers.UserDetailSerializer
    #用户身份设置：是否是登陆用户
    permission_classes = [IsAuthenticated]

    # 重写get_object方法，返回用户详情模型对象
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """更新邮箱"""

    serializer_class = serializers.EmailSerializer

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


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """用户地址新增与修改"""

    serializer_class = serializers.UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 如果这个地址是用户的默认地址，删除用户的默认地址  -----
        if address.user:
            user = request.user
            user.default_address = None
            user.save()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    # 自定义的方法需要使用action装饰器装饰，这样rooter路由就能自动生成
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()

        request.user.default_address = address
        request.user.save()

        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# /browse_histories/
class UserBrowseHistoryView(CreateAPIView):
    """用户浏览记录"""
    # 验证是否登录
    permission_classes = [IsAuthenticated]
    # 指定序列化器
    serializer_class = serializers.UserBrowseHistorySerializer

    def get(self,request):
        """查询浏览记录"""

        """
        获取用户id
        连接redis
        查询redis中的用户浏览记录
        查询sku列表数据
        序列化操作
        响应
        """
        #获取用户id
        user_id = request.user.id
        # 连接redis
        redis_conn = get_redis_connection("history")
        # 查询redis中的用户浏览记录,取前5个
        """
        LRANGE key start stop
        返回列表 key 中指定区间内的元素，区间以偏移量 start 和 stop 指定。
        """
        sku_ids = redis_conn.lrange("history_%s" %user_id,0,4)
        # 查询sku列表数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        # 序列化操作
        s = SKUSerializer(sku_list,many=True)
        print(s.data)

        # 返回
        return Response(s.data)


jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class UserAuthorizeView(ObtainJSONWebToken):
    """
    重写JWT的用户认证
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)

            response = merge_cart_cookie_to_redis(request, response, user)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
