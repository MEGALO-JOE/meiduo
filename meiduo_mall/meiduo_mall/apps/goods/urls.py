from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^categories/(?P<pk>\d+)/$", views.CategoryView.as_view()),  # 面包屑导航

]
