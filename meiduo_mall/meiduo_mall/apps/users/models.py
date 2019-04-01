from django.db import models
from django.contrib.auth.models import AbstractUser

# 这边django自带的用户模型类中没有mobile字段。这百年我们追加mobile字段，并在dev中修改AUTH_USER_MODEL = 'users.User'，指定为我们自己定义的用户模块
class User(AbstractUser):
    """添加"""
    mobile = models.CharField(max_length=11,unique=True,verbose_name="手机号")

    class Meta:
        db_table = "tb_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name


