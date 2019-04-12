from rest_framework import serializers

from .models import GoodsChannel,GoodsCategory,SKU

class ChannelSerializer(serializers.ModelSerializer):
    """一级类别"""
    class Meta:
        model = GoodsChannel
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    """三级类别"""
    class Meta:
        model = GoodsCategory
        fields = "__all__"



class SKUSerializer(serializers.ModelSerializer):
    """SKU列表"""

    class Meta:
        model = SKU
        fields = ["id","name","price","default_image_url","comments"]