from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^carts/$', views.CartView.as_view()),  #增删改查购物车
    # url(r'^cart/$', views..as_view()),  #购物车
]
