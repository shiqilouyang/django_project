"""meiduo_mall URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin

'''
    通过include 函数就可以将两个 urlpatterns 连接起来！

'''
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 手机号验证模块
    url(r'', include('verifications.urls')),
    # 用户登录注册模块
    url(r'', include('users.urls')),
    # 第三方模块，qq
    url(r'oauth/', include('oauth.urls')),
    url(r'', include('area.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^', include('goods.urls')),
    url(r'^', include('carts.urls')),
    url(r'^', include('orders.urls')),

]