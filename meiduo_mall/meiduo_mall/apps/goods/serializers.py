from rest_framework import serializers

from .models import GoodsChannel,GoodsCategory

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
