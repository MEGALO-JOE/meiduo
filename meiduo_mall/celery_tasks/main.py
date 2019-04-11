# celery启动文件

from celery import Celery
import os


# 在发送邮件的异步任务中，需要用到django的配置文件，所以我们需要修改celery的启动文件main.py，在其中指明celery可以读取的django配置文件，并且注册添加email的任务
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 创建celery实例
celery_app = Celery('meiduo')

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email','celery_tasks.html'])