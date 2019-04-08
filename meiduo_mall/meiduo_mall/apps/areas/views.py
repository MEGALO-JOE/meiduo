from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Areas
from . import serializers

# Create your views here.
class AreasViewSet(ReadOnlyModelViewSet):
    """省份视图"""

    def get_queryset(self):
        """提供数据"""

        if self.action == "list":
            return Areas.objects.filter(parent=None)
        else:
            return Areas.objects.all()

    def get_serializer_class(self):
        """提供序列化器"""

        if self.action == "list":
            return serializers.AreaSerializer
        else:
            return serializers.SubsSerializer


