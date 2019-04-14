from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),  #订单结算
    url(r'^orders/$', views.OrderSaveView.as_view()),  #下单，保存订单
]
