from rest_framework import serializers

from .models import Areas


class AreaSerializer(serializers.ModelSerializer):
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