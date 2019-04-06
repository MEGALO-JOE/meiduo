from django.db import models


class BaseModel(models.Model):
    """为模型类型补充字段"""

    creae_time = models.DateField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateField(auto_now=True,verbose_name="修改时间")

    class Meta:

        #说明是抽象类型，迁移时不会创建BaceModel表
        abstract = True