from rest_framework import serializers
from django_redis import get_redis_connection

from .utils import generate_real_openid
from .models import OAuthQQUser
from users.models import User


class UserOpenidSerializer(serializers.Serializer):
    """用户和openid的绑定序列化器"""

    access_token = serializers.CharField(label="操作凭证")
    mobile = serializers.RegexField(label="手机号",regex=r"^1[3-9]{9}")
    password = serializers.CharField(label="密码",max_length=20,min_length=8)
    sms_code = serializers.CharField(label="短信验证码")

    # 校验
    def validate(self, attrs):
        # 检测access_token
        access_token = attrs.get("access_token")
        if not access_token:
            raise serializers.ValidationError("缺少access_token参数")
        # 获取openid
        openid = generate_real_openid(access_token)
        if not openid:
            raise serializers.ValidationError("无效的access_token")

        attrs["openid"] = openid

        # 校验短信验证码
        mobile = attrs.get("mobile")
        sms_code = attrs.get("sms_code")
        password = attrs.get("password")
        if not all([mobile,sms_code,password]):
            raise serializers.ValidationError("参数不全")

        redis_conn = get_redis_connection("verify_codes")
        real_sms_code = redis_conn.get("sms_cod_%s" % mobile)


        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError("短信验证码错误")

        # 如果用户存在，检查密码
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
           return attrs

        # print(user)

        if not user.check_password(password):
            raise serializers.ValidationError("密码错误")

        attrs["user"] = user

        return attrs

    def create(self, validated_data):
        """获取校验用户"""
        user = validated_data.get("user")

        if not user:
            # 用户不存在，创建新的用户
            user = User()
            user.mobile = validated_data.get("mobile")
            user.username = validated_data.get("mobile")
            user.set_password(validated_data.get("password"))

        # 这边一定记得保存
        user.save()
        # 将用户和openid绑定
        OAuthQQUser.objects.create(
            openid = validated_data.get("openid"),
            user = user
        )


        return user