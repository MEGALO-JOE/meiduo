from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from . models import GoodsCategory
from .serializers import ChannelSerializer,CategorySerializer

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

#
# class CategoriesView(APIView):
#     """获取当前分类信息"""
#
#     def get(self,request, pk):
#         """
#         1.获取前端数据
#         2. 查询当前三级分类信息
#         3.通过三级分类信息获取一二集分类
#         4. 返回
#         :param request:
#         :return:
#         """
#         cat3 = GoodsCategory.objects.get(id=pk) # 获取三级
#         cat2 = cat3.parent  # 自关联获取二级,
#         cat1 = cat2.parent  # 自关联获取一级
#
#         data = {
#             "cat1": cat1.name,
#             "cat2": cat2.name,
#             "cat3": cat3.name
#         }
#
#         print(data)
#
#         # 返回数据
#         return Response(data=data)
