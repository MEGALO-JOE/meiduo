from decimal import Decimal
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer, SaveOrderSerializer


class OrderSettlementView(APIView):
    """订单结算"""

    # 只允许登陆用户访问
    permission_classes = [IsAuthenticated]

    def get(self,request):

        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection("carts")
        redis_cart = redis_conn.hgetall("cart_%s" %user.id)
        redis_select = redis_conn.smembers('selected_%s' % user.id)

        cart = {}
        for sku_id in redis_select:
            cart[int(sku_id)] = int(redis_cart[sku_id])


        """
        redis
            hash：商品和数量
                键：cart_user.id
                值：{"sku_id":"count","sku_id":"count",...}
            set:勾选
                键：select_sku_id
                值：{sku_id1,sku_id2,...}
        """
        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            # 给字段新增加count值
            sku.count = cart[sku.id]

        # 运费
        freight = Decimal('10.00')

        # 序列化
        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        # 返回
        return Response(serializer.data)


class OrderSaveView(CreateAPIView):
    """保存订单"""

    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer


