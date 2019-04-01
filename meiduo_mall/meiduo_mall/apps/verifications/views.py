from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from random import randint
import logging
from rest_framework.response import Response
from rest_framework import status


from . import constants
from celery_tasks.sms.tasks import send_sms_code


class SMSCodeView(APIView):
    """发送短信验证码视图"""

    def get(self,request,mobile):

        # 创建redis连接对象
        redis_conn = get_redis_connection("verify_codes")

        # 为避免客户重复发送短信，这比做个限制
        send_flag = redis_conn.get("send_flag_%s" % mobile)

        if send_flag:
            return Response(data={"message":"短信发送频繁！"},status=status.HTTP_400_BAD_REQUEST)

        # TODO 验证手机是否已经注册

        # 生成验证码
        SMS_code = "06%d" % randint(0,999999)
        logger = logging.getLogger('django')
        logger.info("SMS_code:%s " % SMS_code)


        # # 将验证码存入redis中
        # redis_conn.setex("sms_cod_%s" % mobile,constants.SMS_CODE_REDIS_EXPIRES,SMS_code)
        # # 存储一个标记，表示这个手机已经发送国验证码类，有效期60s
        # redis_conn.setex("send_flag_%s" % mobile,constants.SEND_SMS_CODE_INTERVAL,1)

        """
        redis pipeline的使用
            1.目的
                利用管道让多条Redis命令一起一次执行,避免多条命令多次访问Redis数据库
            
            2.注意点
                在使用pipeline时，记得调用 execute() 执行一下
        
        """
        # 创建管道
        pl = redis_conn.pipeline()
        # 将验证码存入redis中
        pl.setex("sms_cod_%s" % mobile,constants.SMS_CODE_REDIS_EXPIRES,SMS_code)
        # 存储标记
        pl.setex("send_flag_%s" % mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        # 执行
        pl.execute()

        # 发送短信
        # CCP().send_template_sms(mobile,[SMS_code,constants.SMS_CODE_REDIS_EXPIRES // 60],1)

        """
        发送短信受网络的影响，因为前端是在接收到Response返回数据时，才去调用哪个倒计时的效果，
        所以使用celery异步发送短信
        
        """
        send_sms_code.delay(mobile,SMS_code)



        return Response(data={"message":"ok"})