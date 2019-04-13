from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """购物车序列化器:校验数据使用"""

    # 定义字段
    sku_id = serializers.IntegerField(label='商品 SKU ID', min_value=1)
    count = serializers.IntegerField(label='商品数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate_sku_id(self, value):
        """校验sku_id"""
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id 不存在')

        return value

class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')