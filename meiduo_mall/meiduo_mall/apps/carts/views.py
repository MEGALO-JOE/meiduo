from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework import status
import base64, pickle

from goods.models import SKU
from . import serializers
from meiduo_mall.utils.CartCookieCoder import set_cart_cookie_str, get_cart_cookie_dict


# Create your views here.
class CartView(APIView):
    """用户购物车"""

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        保证用户未登录也可以进入下面的请求方法
        """
        pass

    def post(self, request):
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

        resopnse = Response(serializer.data, status=status.HTTP_201_CREATED)
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
            pl.hincrby("cart_%s" % user.id, sku_id, count)

            pl.execute()
        else:
            # 用户未登陆
            # 获取购物车数据
            cookie_cart_str = request.COOKIES.get("cart")
            if not cookie_cart_str:
                # 没有购物车，创建一个
                carts_dict = {}
            else:
                # # 把字条串转换成bytes类型的字符串
                # cart_str_bytes = cookie_cart_str.encode()
                # # 把bytes类型的字符串转换成bytes类型
                # cart_bytes = base64.b64decode(cart_str_bytes)
                # # 把bytes类型转换成字典
                # carts_dict = pickle.loads(cart_bytes)

                carts_dict = get_cart_cookie_dict(cookie_cart_str)


            # 判断要加入的商品是否已经存在在购物车
            if sku_id in carts_dict:
                # 存在做增量
                origin_count = carts_dict[sku_id]["count"]
                count += origin_count

            carts_dict[sku_id] = {
                "count": count,
                "selected": selected
            }

            cookie_carts_str = set_cart_cookie_str(carts_dict)

            resopnse.set_cookie("cart", cookie_carts_str)

        return resopnse

    def get(self, request):
        """获取购物车"""

        # 判断用户是否登陆
        try:
            user = request.user
        except Exception as e:
            user = None

        if user and user.is_authenticated:
            # 用户已登陆,获取redis中的购物车数据,和勾选状态
            redis_conn = get_redis_connection("carts")
            """
            HGETALL key
            返回哈希表 key 中，所有的域和值。            
            在返回值里，紧跟每个域名(field name)之后是域的值(value)，所以返回值的长度是哈希表大小的两倍。
            SMEMBERS key
            返回集合 key 中的所有成员。
            不存在的 key 被视为空集合。
            """
            redis_cart = redis_conn.hgetall("cart_%s" % user.id)
            redis_selected = redis_conn.smembers("selected_%s" % user.id)

            # 将redis中的两个数据统一格式，跟cookie中的格式一致，方便统一查询
            carts_dict = {}
            for sku_id, count in redis_cart.items():
                carts_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }

        else:
            # 用户未登陆，取出cookie中的购物车数据
            cookie_cart_str = request.COOKIES.get("cart")

            # 将cookie中的cart转换成字典
            if cookie_cart_str:
                carts_dict = get_cart_cookie_dict(cookie_cart_str)
            else:
                carts_dict = {}

        # 查询购物车数据
        sku_ids = carts_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        # 补充count和selected字段
        for sku in skus:
            sku.count = carts_dict[sku.id]['count']
            sku.selected = carts_dict[sku.id]['selected']

        # 创建序列化器序列化商品数据
        serializer = serializers.CartSKUSerializer(skus, many=True)

        # 响应结果
        return Response(serializer.data)

    def put(self, request):
        """更改购物车"""
        # 判断用户是否登陆
        try:
            user = request.user
        except Exception as e:
            user = None

        # 创建序列化器并校验
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验后的数据
        sku_id = serializer.validated_data.get("sku_id")
        count = serializer.validated_data.get("count")
        selected = serializer.validated_data.get("selected")

        response = Response(serializer.data)
        carts_dict = {}
        # 判断用户是否登录
        if user and user.is_authenticated:
            # 创建连接到redis对象
            redis_conn = get_redis_connection('carts')
            # 管道
            pl = redis_conn.pipeline()
            """
            1.概念
            	非幂等
		            如果后端处理结果对于这些请求的最终结果不同，跟请求次数相关，则称接口非幂等
	            幂等
		            对于同一个接口，进行多次相同的请求，如果后端处理结果对于这些请求都是相同的，则称接口是幂等的

            HSET key field value
            将哈希表 key 中的域 field 的值设为 value 。
            如果 key 不存在，一个新的哈希表被创建并进行 HSET 操作。            
            如果域 field 已经存在于哈希表中，旧值将被覆盖。
            """
            # 因为接口设计为幂等的，直接覆盖
            pl.hset('cart_%s' % user.id, sku_id, count)
            # 是否选中
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()

        else:
            cookie_cart_str = request.COOKIES.get("cart")

            if cookie_cart_str:
                carts_dict = get_cart_cookie_dict(cookie_cart_str)
            else:
                return Response({'message': '没有获取到cookie'}, status=status.HTTP_400_BAD_REQUEST)

            # 直接覆盖原cookie字典数据
            carts_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 把cookie大字典再转换字符串
            # cart_str = base64.b64encode(pickle.dumps(carts_dict)).decode()
            cookie_cart_str = set_cart_cookie_str(carts_dict)
            # # 创建响应对象
            # response = Response(serializer.data)
            # 设置cookie
            response.set_cookie('cart', cookie_cart_str)

        return response

    def delete(self, request):
        """删除购物车"""

        # 创建序列化器并校验
        serializer = serializers.CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验后的数据
        sku_id = serializer.validated_data.get("sku_id")

        if not sku_id:
            return Response({"message":"操作错误，你购物车中没有此件商品"},status=status.HTTP_400_BAD_REQUEST)

        # 判断是否登陆
        try:
            user = request.user
        except Exception:
            user = None

        response = Response(status=status.HTTP_204_NO_CONTENT)
        if user and user.is_authenticated:
            # 登陆用户，取出redis数据删除购物
            redis_conn = get_redis_connection("carts")
            pl = redis_conn.pipeline()

            # 删除健就等于删除了整条记录
            pl.hdel('cart_%s' % user.id,sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

        else:
            cookie_cart_str = request.COOKIES.get("cart")

            if cookie_cart_str:
                carts_dict = get_cart_cookie_dict(cookie_cart_str)
            else:
                carts_dict = {}

            if sku_id in carts_dict:
                del carts_dict[sku_id]

                cookie_cart_str = set_cart_cookie_str(carts_dict)

                response.set_cookie("cart",cookie_cart_str)

        return response


class CartSelectedAllView(APIView):
    """购物车全选"""

    def perform_authentication(self, request):

        pass

    def put(self, request):
        """购物车全选"""

        serializer = serializers.CartSelectedAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selection = serializer.validated_data.get("selected")

        try:
            user = request.user
        except:
            user = None

        response = Response(serializer.data)
        if user and user.is_authenticated:

            redis_conn = get_redis_connection("carts")
            # 获取hash字典中的所有数据
            cart_redis_dict = redis_conn.hgetall('cart_%d' % user.id)
            # 把hash字典中的所有key
            sku_ids = cart_redis_dict.keys()
            # 判断当前selected是True还是False
            if selection:
                # 如果是True 就把所有sku_id 添加到set集合中 *[1, 2, 3]
                redis_conn.sadd('selected_%d' % user.id, *sku_ids)
            else:
                # 如果是False 就把所有sku_id 从set集合中删除
                redis_conn.srem('selected_%d' % user.id, *sku_ids)

        else:

            cookie_cart_str = request.COOKIES.get("cart")

            if not cookie_cart_str:
                return Response({'message': 'cookie 没有获取到'}, status=status.HTTP_400_BAD_REQUEST)

            carts_dict = get_cart_cookie_dict(cookie_cart_str)

            for sku_id in carts_dict:
                carts_dict[sku_id]["selected"] = selection

            cookie_cart_str = set_cart_cookie_str(carts_dict)

            response.set_cookie("cart",cookie_cart_str)

        return response








