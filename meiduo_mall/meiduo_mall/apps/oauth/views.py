from django.shortcuts import render
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_jwt.settings import api_settings
from itsdangerous import BadData

from carts.utils import merge_cart_cookie_to_redis
from .models import OAuthQQUser,User
from .utils import generate_save_user_openid_token
from .serializers import UserOpenidSerializer
import logging
logger = logging.getLogger('django')


# http://api.meiduo.com:8000/oauth/qq/authorization/?next=/
class QQOauthURLView(GenericAPIView):
    """提供qq登陆页面网址"""

    def get(self,request):
        """next表示从哪个页面进入登陆页面，奖励啊登陆成功后就回到哪个页面"""

        next = request.query_params.get("next","/")

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,client_secret=settings.QQ_CLIENT_SECRET,redirect_uri=settings.QQ_REDIRECT_URI,state=next)

        login_url = oauth.get_qq_url()

        print(login_url)

        return Response({"login_url":login_url},status=status.HTTP_200_OK)

# url(r'^qq/user/$', views.QQAuthUserView.as_view()),
class QQAuthUserView(GenericAPIView):
    """用户扫码登录的回调处理"""

    serializer_class = UserOpenidSerializer

    def get(self, request):
        # 提取code请求参数
        code = request.query_params.get("code")
        if not code:
            return Response({"messgae":"缺少必要参数code"},status=status.HTTP_400_BAD_REQUEST)
        # 使用code向QQ服务器请求access_token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,client_secret=settings.QQ_CLIENT_SECRET,redirect_uri=settings.QQ_REDIRECT_URI,state=next)
        try:
            access_token = oauth.get_access_token(code)
            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.info(e)
            return Response({"message":"qq服务器异常"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 使用openid查询该QQ用户是否在美多商城中绑定过用户
        try:
            oauthqquser_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果openid没绑定美多商城用户，创建用户并绑定到openid
            # 为了能够在后续的绑定用户操作中前端可以使用openid，在这里将openid签名后响应给前端
            try:
                access_token_openid = generate_save_user_openid_token(openid)
            except BadData:
                return None


            return Response({"access_token":access_token_openid})

        else:
            # 如果openid已绑定美多商城用户，直接生成JWT token，并返回
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 获取关联的user
            user = oauthqquser_model.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                "token":token,
                "user_id":user.id,
                "username":user.username
            })

            # 合并购物车
            response = merge_cart_cookie_to_redis(request,response,user)

            return response


    def post(self,request):
        """openid绑定用户接口"""

        # 获取序列化对象
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # 保存校验结果并接收
        user = serializer.save()

        # print(user)

        # 生成JWT token 并响应，因为要做状态保持
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            "token":token,
            "user_id":user.id,
            "username":user.username
        })

        # 合并购物车
        response = merge_cart_cookie_to_redis(request,response,user)

        return response


