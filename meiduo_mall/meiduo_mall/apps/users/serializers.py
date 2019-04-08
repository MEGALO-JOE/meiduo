from rest_framework import serializers
import re
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from .models import User,Address
from celery_tasks.email.tasks import send_verify_email


class UserRegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""

    # 分析

    # 序列化器的所有字段: ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    # 需要校验的字段: ['username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    # 模型中已存在的字段: ['id', 'username', 'password', 'mobile']

    # 需要序列化的字段: ['id', 'username', 'mobile', 'token']
    # 需要反序列化的字段: ['username', 'password', 'password2', 'mobile', 'sms_code', 'allow']
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)  # 'true'
    # 加入JWT，解决跨域身份验证
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = User

        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow','token']
        # 因为django自带的用户模型类中定义的password和username都不能满足我们的需求，所以这边做个修改
        extra_kwargs = {  # 修改字段选项
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {  # 自定义校验出错后的错误信息提示
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }

            }
        }

    # 校验
    # 校验手机号码
    def validate_mobild(self, value):

        if not re.match(r"1[3-9]\d{9}",value):
            raise serializers.ValidationError("手机号码格式错误")

        return value

    # 检验是否同意协议
    def validate_allow(self,value):
        if value != "true":
            raise serializers.ValidationError("请勾选美多商城用户使用协议")

        return value

    # 检验验证码和密码
    def validate(self, attrs):
        # 检验密码是否相同
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("两次密码不一致")

        # 检验验证码
        redis_conn = get_redis_connection("verify_codes")
        mobile = attrs["mobile"]
        # edis存储数据时是以字符串存储的，取出来后元素都是bytes类型
        real_sms_code = redis_conn.get("sms_cod_%s" % mobile).decode()

        if attrs["sms_code"] != real_sms_code:
            raise serializers.ValidationError("验证码错误")

        return attrs

    # 由于要把不需要存储的 password2, sms_code, allow 从字段中移除，所以重写create方法
    # validated_data:["password","mobile","username"]
    def create(self, validated_data):
        del validated_data["password2"]
        del validated_data["sms_code"]
        del validated_data["allow"]

        # 密码需要加密后存储，先取出密码，然后仔调用加密进行存储
        password = validated_data.pop("password")

        # 创建user'模型对象，给其中的username和mobile赋值
        user = User(**validated_data)
        user.set_password(password)  #加密并保存
        user.save()

        # 签发JWT
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""

    class Meta:
        model = User
        fields = ("id","username","mobile","email","email_active")


class EmailSerializer(serializers.ModelSerializer):
    """邮箱序列化"""

    class Meta:
        model = User
        fields = ("id","email")
        extra_kwargs = {
            "email":{
                "required":True
            }
        }

    def update(self, instance, validated_data):
        """重写这个方法不是为了修改，而是为了发送激活邮件"""

        instance.email = validated_data.get("email")
        instance.save()

        #发送激活邮件
        verify_url = instance.generate_verify_email_url()
        send_verify_email.delay(instance.email,verify_url=verify_url)

        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """
        用户地址序列化器
        """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        # 除下面之外
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user  #核心代码
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """

    class Meta:
        model = Address
        fields = ('title',)
