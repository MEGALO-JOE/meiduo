from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^carts/$', views.CartView.as_view()),  #增删改查购物车

    url(r'^cart/selection/$', views.CartSelectedAllView.as_view()),  # 全选按钮
]
