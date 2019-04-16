from django.shortcuts import render
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status

from . models import GoodsCategory,SKU
from .serializers import ChannelSerializer, CategorySerializer, SKUSerializer, SKUSearchSerializer


class CategoryView(GenericAPIView):
    """
    商品列表页面包屑导航
    """
    queryset = GoodsCategory.objects.all()

    def get(self, request, pk=None):
        ret = dict(
            cat1='',
            cat2='',
            cat3=''
        )
        category = self.get_object()
        if category.parent is None:
            # 当前类别为一级类别
            ret['cat1'] = ChannelSerializer(category.goodschannel_set.all()[0]).data
        elif category.goodscategory_set.count() == 0:
            # 当前类别为三级
            ret['cat3'] = CategorySerializer(category).data
            cat2 = category.parent
            ret['cat2'] = CategorySerializer(cat2).data
            ret['cat1'] = ChannelSerializer(cat2.parent.goodschannel_set.all()[0]).data
        else:
            # 当前类别为二级
            ret['cat2'] = CategorySerializer(category).data
            ret['cat1'] = ChannelSerializer(category.parent.goodschannel_set.all()[0]).data

        return Response(ret)


class SKUListView(ListAPIView):
    """SKU商品分页"""

    serializer_class = SKUSerializer

    # 指定过滤后端为排序过滤
    filter_backends = (OrderingFilter,)

    ordering_fields = ("create_time","price","sales")

    def get_queryset(self):
        """
        如果当前在视图中没有去定义get /post方法 那么就没法定义一个参数用来接收正则组提取出来的url路径参数,
        可以利用视图对象的 args或kwargs属性去获取啊
        :return:
        """
        category_id = self.kwargs.get("category_id")

        if not category_id:
            return Response({"message":"参数错误"},status=status.HTTP_400_BAD_REQUEST)
        # is_launched 上架的
        return SKU.objects.filter(category_id=category_id,is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]  # 指定查询集

    serializer_class = SKUSearchSerializer  # 指定序列化器