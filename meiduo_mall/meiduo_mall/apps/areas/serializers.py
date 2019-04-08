from rest_framework import serializers
from rest_framework_extensions.cache.mixins import CacheResponseMixin  #加入缓存

from .models import Areas


class AreaSerializer(CacheResponseMixin,serializers.ModelSerializer):
    """省份序列化器"""

    class Meta:
        model = Areas
        fields = ["id","name"]



class SubsSerializer(serializers.ModelSerializer):
    """省区序列化器"""

    subs = AreaSerializer(many=True,read_only=True)

    class Meta:
        model = Areas
        fields = ["id","name","subs"]