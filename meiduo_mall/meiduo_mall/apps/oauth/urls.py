from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/authorization/$', views.QQOauthURLView.as_view()),  #qq登陆页面网址
    url(r'^qq/user',views.QQAuthUserView.as_view()),  #qq登陆后回调地址
]
