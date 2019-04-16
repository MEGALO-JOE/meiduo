from django.conf.urls import url

from . import views

urlpatterns = [
    # 支付宝支付
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.PaymentView.as_view()),
    # 支付后验证状态
    url(r'^payment/status/$', views.PaymentStatusView.as_view()),

]