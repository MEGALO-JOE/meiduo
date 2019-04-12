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
        # 千万不要少了这一行,不然admin的保存就无效
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


class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku  # 通过外键获取图片模型对象所关联的sku模型的id
        # 如果商品还有默认图片，就设置一张
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url  # ImageField 这个属性默认有个url方法可以取到
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)

admin.site.register(models.GoodsCategory,GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU,SKUAdmin)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage,SKUImageAdmin)
