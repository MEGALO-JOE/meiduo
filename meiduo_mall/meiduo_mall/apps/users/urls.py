from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^users/$', views.UserRegisterView.as_view()), #用户注册
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),#判断用户名是否已经存在
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.UserMobileView.as_view()),  # 判断手机号码是否已经注册

]
