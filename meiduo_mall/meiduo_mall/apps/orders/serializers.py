from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from django_redis import get_redis_connection
import logging
import time

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods

logger = logging.getLogger('django')

class CartSKUSerializer(serializers.ModelSerializer):
    """商品购物车序列化器"""

    count = serializers.IntegerField(label="数量")

    class Meta:
        model = SKU
        fields = ["id","name","default_image_url","price","count"]

class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    """
    下单数据序列化器
    """

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """保存订单"""
        # 获取当前下单用户
        # 生成订单编号
        # 保存订单基本信息数据 OrderInfo
        # 从redis中获取购物车结算商品数据
        # 遍历结算商品：
            # 判断商品库存是否充足
            # 减少商品库存，增加商品销量
            # 保存订单商品数据
        # 在redis购物车中删除已计算商品数据

        # 获取当前下单用户
        user = self.context["request"].user

        # 生成订单编号  组织订单编号 20170903153611+user.id
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        address = validated_data["address"]
        pay_method = validated_data["pay_method"]

        # 保存订单基本信息数据 OrderInfo
        # 这边采取数据库的事务功能，因为这边设计几张表，所以，只有再全部数据正常执行时，才能写入数据
        # 开启事务
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()

            # 捕获整个过程中所产生的错误
            try:
                # 创建订单信息
                order = OrderInfo.objects.create(
                    order_id = order_id,
                    user = user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal(0),
                    freight = Decimal(10),
                    pay_method = pay_method,
                    status=(OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                            if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']
                            else OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
                )

                # 获取购物车信息
                redis_conn = get_redis_connection("carts")
                redis_cart = redis_conn.hgetall("cart_%s" % user.id)
                redis_selected = redis_conn.smembers('selected_%s' % user.id)

                # 将byte类型转换成int类型
                cart = {}
                for sku_id in redis_cart:
                    cart[int(sku_id)] = int(redis_cart[sku_id])

                # 一次查询出所有商品数据
                skus = SKU.objects.filter(id__in=cart.keys())

                # 处理订单商品
                for sku in skus:

                    while True: # 让用户对同一个商品有无限次下单机会,只到库存真的不足为止
                        sku_count = cart[sku.id]

                        # 判断库存
                        origin_stock = sku.stock  # 原始库存
                        origin_sales = sku.sales  # 原始销量

                        # time.sleep(8)

                        if sku_count > origin_stock:
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError('商品库存不足')

                        # 减少库存
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count



                        result = SKU.objects.filter(stock=origin_stock, id=sku.id).update(stock=new_stock,
                                                                                                sales=new_sales)
                        if result == 0:  # 如果没有修改成功,说明有抢夺
                            continue  #跳过这次循环，下面不会执行

                        sku.stock = new_stock
                        sku.sales = new_sales
                        sku.save()

                        # 累计商品的SPU 销量信息
                        sku.goods.sales += sku_count
                        sku.goods.save()

                        # 累计订单基本信息的数据
                        order.total_count += sku_count  # 累计总数量
                        order.total_amount += (sku.price * sku_count)  # 累计总额

                        # 保存订单商品
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        break  # 当前这个商品下单成功,跳出死循环,进行对下一个商品下单


                # 更新订单的金额数量信息
                order.total_amount += order.freight
                order.save()

            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('商品库存不足')


            # 提交事务
            transaction.savepoint_commit(save_id)

            # 更新redis中保存的购物车数据
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, *redis_selected)
            pl.srem('selected_%s' % user.id, *redis_selected)
            pl.execute()


            return order
