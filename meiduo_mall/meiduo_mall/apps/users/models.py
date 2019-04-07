from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings

from . import constants

# 这边django自带的用户模型类中没有mobile字段。这百年我们追加mobile字段，并在dev中修改AUTH_USER_MODEL = 'users.User'，指定为我们自己定义的用户模块
class User(AbstractUser):
    """添加"""
    mobile = models.CharField(max_length=11,unique=True,verbose_name="手机号")
    email_active = models.BooleanField(default=False,verbose_name="邮箱验证码")

    class Meta:
        db_table = "tb_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name


    def generate_verify_email_url(self):
        """生成验证邮箱的url"""

        # 1.创建加密序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)

        # 2.调用dumps方法进行加密, bytes
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()

        # 3.拼接激活url
        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

    @staticmethod
    def check_verify_email_token(token):
        """对token解密并查询对应的user"""
        # 1.创建加密序列化器
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        # 2.调用loads解密
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            id = data.get('user_id')
            email = data.get('email')
            try:
                user = User.objects.get(id=id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user