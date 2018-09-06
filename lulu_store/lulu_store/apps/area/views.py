from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView

# Create your views here.
from rest_framework_extensions.cache.decorators import cache_response

from area.models import Area
from area.serializers import AreaSerializer, SubAreaSerializer

'''查询行政区信息，页面加载即要返回数据！'''


class AreasViewSet(ListAPIView):
    serializer_class = AreaSerializer
    # 第一种指定查询集的方式，返回的是 Area 没有自关联外键的！
    queryset = Area.objects.filter(parent_id=None)
    # 指定查询对象集对象！不使用默认的全部返回的形式！
    # def get_queryset(self):
    #     return Area.objects.filter(parent_id=None)


'''查询自行政区的信息，当点击事件触发！
    如果使用了 RetrieveAPIView 就要更改默认的查询集
'''


class AreasViewSets(RetrieveAPIView):
    serializer_class = SubAreaSerializer

    # 第一种指定查询集的方式！
    # queryset = Area.objects.all()

    # 第二种指定返回数据集合的方式！
    def get_queryset(self):
        return Area.objects.all()

    # 使用装饰器，说明第一次查询在mysql之中查询，第二次查询在 redis之中查询
    # 设置存储在 'default' redis库之中！
    @cache_response(key_func='calculate_cache_key')
    def get(self, request, *args, **kwargs):
        return super().get(self, request, *args, **kwargs)

    def calculate_cache_key(self, view_instance, view_method,
                            request, args, kwargs):
        pk = self.kwargs['pk']
        pk_list = []
        pk_list.append(pk)
        return '.'.join(pk_list)
