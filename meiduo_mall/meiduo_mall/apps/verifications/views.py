from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from random import randint
import logging
from rest_framework.response import Response
from rest_framework import status

from meiduo_mall.libs.yuntongxun.sms import CCP
from . import constants


class SMSCodeView(APIView):
    """发送短信验证码视图"""

    def get(self,request,mobile):

        # 创建redis连接对象
        redis_conn = get_redis_connection("verify_codes")

        # 为避免客户重复发送短信，这比做个限制
        send_flag = redis_conn.get("send_flag_%s" % mobile)

        if send_flag:
            return Response({"message":"短信发送频繁！"},status=status.HTTP_400_BAD_REQUEST)


        # 生成验证码
        SMS_code = "06%d" % randint(0,999999)
        logger = logging.getLogger('django')
        logger.info("SMS_code:%s " % SMS_code)

        # 将验证码存入redis中
        redis_conn.setex("sms_cod_%s" % mobile,constants.SMS_CODE_REDIS_EXPIRES,SMS_code)
        # 存储一个标记，表示这个手机已经发送国验证码类，有效期60s
        redis_conn.setex("send_flag_%s" % mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        # 发送短信
        CCP().send_template_sms(mobile,[SMS_code,constants.SMS_CODE_REDIS_EXPIRES // 60],1)

        data = {
            "message":"ok"
        }

        return Response(data=data)