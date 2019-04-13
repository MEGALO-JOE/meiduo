from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework import status
import base64,pickle

from . import serializers

# Create your views here.
class CartView(APIView):
    """用户购物车"""

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        保证用户未登录也可以进入下面的请求方法
        """
        pass

    def post(self,request):
        """添加购物车"""

        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取校验后的数据
        sku_id = serializer.validated_data.get("sku_id")
        count = serializer.validated_data.get("count")
        selected = serializer.validated_data.get("selected")

        """
        判断用户是否登陆
        用户登陆；
            操作reids数据库存储购物车
            连接redis数据库
            新增选中状态
            返回        
        """
        try:
            user = request.user
        except Exception as e:
            user = None

        resopnse = Response(serializer.data,status=status.HTTP_201_CREATED)
        if user and user.is_authenticated:
            """表示登陆用户"""
            redis_conn = get_redis_connection("carts")
            pl = redis_conn.pipeline()

            """
            HINCRBY key field increment            
            为哈希表 key 中的域 field 的值加上增量 increment 。            
            增量也可以为负数，相当于对给定域进行减法操作。            
            如果 key 不存在，一个新的哈希表被创建并执行 HINCRBY 命令。            
            如果域 field 不存在，那么在执行命令前，域的值被初始化为 0 。            
            对一个储存字符串值的域 field 执行 HINCRBY 命令将造成一个错误。            
            本操作的值被限制在 64 位(bit)有符号数字表示之内。
            """
            # 新增购物车数据
            pl.hincrby("cart_%s" %user.id,sku_id,count)
            # 新增选中状态
            if selected:
                pl.sadd("selected_%s" %user.id,sku_id)

            pl.execute()
        else:
            # 用户未登陆
            # 获取购物车数据
            carts_str = request.COOKIES.get("cart")
            if not carts_str:
                # 没有购物车，创建一个
                carts_dict = {}
            else:
                # 有购物车 ，将cookie中取到的carts_str转换成bytes，再将bytes转换成bace64的bytes，最后将bytes转成字典
                carts_dict = pickle.loads(base64.b64decode(carts_str.decode()))

            # 判断要加入的商品是否已经存在在购物车
            if sku_id in carts_dict:
                # 存在做增量
                origin_count = carts_dict[sku_id]["count"]
                count += origin_count

            carts_dict[sku_id] = {
                "count":count,
                "selected":selected
            }

            # 将字段转换成bytes，再将bytes转换成bace64的bytes，最后将bytes转换成字符串返回给cookie
            # 先将字典转换成bytes类型
            cart_bytes = pickle.dumps(carts_dict)
            # 再将bytes类型转换成bytes类型的字符串
            cart_str_bytes = base64.b64encode(cart_bytes)
            # 把bytes类型的字符串转换成字符串
            cookie_carts_str = cart_str_bytes.decode()

            resopnse.set_cookie("cart",cookie_carts_str)

        return resopnse


    def get(self,request):
        """获取购物车"""
        pass

    def put(self,request):
        """更改购物车"""
        pass

    def delete(self,request):
        """删除购物车"""
        pass


