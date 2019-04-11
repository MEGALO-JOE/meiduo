from django.contrib import admin

from . import models


# Register your models here.
class GoodsCategoryAdmin(admin.ModelAdmin):
    """商品类别模型站点管理类"""

    def save_model(self, request, obj, form, change):
        """
        当点击admin中的保存按钮时会来调用此方法
        :param request:保存时本次请求对象
        :param obj:本次要保存的模型对象
        :param form:admin中的表单
        :param change: 是否更改  bool
        """

        obj.save()
        # 重新生成静态页面  因为时耗时操作，所以选用异步
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()

    def delete_model(self, request, obj):
        """
        当点击admin中的删除按钮时会来调此方法
        :param request: 删除时本次请求对象
        :param obj: 本次要删除的对象
        """

        obj.delete()
        # 重新生成静态页面
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()



admin.site.register(models.GoodsCategory,GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
