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
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
    url(r'^browse_histories/$', views.UserBrowsingHistoryView.as_view()),
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),

]
router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls


# http://api.meiduo.site:8000/categories/115/skus/?page=2&page_size=5&ordering=-create_time