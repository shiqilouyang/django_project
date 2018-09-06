""" URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    # url(r'^$', views.home, name='home'),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),

    url(r'^users/$', views.UserView.as_view()),
    # 用户登录，被封装起来，直接指向模块文件！如果只是返回 token，不需要重写，还要增加其他信息，在setting指向！
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^emails/$', views.EmailView.as_view()),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    url(r'^addresses/$', views.AddressViewSet.as_view()),
    # 删除用户，用户值改为 is_delete 改为 Ture
    url(r'^addresses/(?P<pk>\d+)/$', views.AddressViewSet.as_view()),
    # 设置默认值操作！
    url(r'^addresses/(?P<pk>\d+)/status/$', views.AddressViewSet.as_view()),
    url(r'^addresses/(?P<pk>\d+)/title/$', views.AddressViewSetDefault.as_view()),

]
# router = routers.DefaultRouter()
# router.register(r'addresses', views.AddressViewSet, base_name='addresses')
#
# urlpatterns += router.urls
