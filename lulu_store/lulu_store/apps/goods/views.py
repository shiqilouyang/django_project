from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView
# Create your views here.
from django_redis import get_redis_connection

from rest_framework.response import Response
# 指定排序方法！
from rest_framework.filters import OrderingFilter
from goods.models import Goods, SKU
from goods.serializer import SKUSerializer, AddUserBrowsingHistorySerializer, SKUIndexSerializer
from lulu_store.utils.pagination import StandardResultsSetPagination
# 使用索引模块自带的视图集
from drf_haystack.viewsets import HaystackViewSet

'''展示热销产品'''

class HotSKUListView(ListAPIView):
    '''
        GET /categories/(?P<category_id>\d+)/hotskus/
        分析过程！
            1,由于包含查询操作，也就是序列化的过程，需要定义序列化器！
            2,查询是根据商品类进行查询操作！不是单一数据操作，因此采用 get_queryset()
            3,指定返回集合，只返回已经上架的商品集合！
    '''
    serializer_class = SKUSerializer
    # 不能在此处使用分页操作！由于全局定义了分页，因此 ListAPIView会按照分页进行使用！
    pagination_class = None

    # list 查询返回多个数据一般与 get_queryset一起使用！
    def get_queryset(self):
        # self.kwargs 是个字典 当调用 as_view() 是产生的属性！在 最顶层 view之中赋值！
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:4]


'''历史浏览记录显示！'''
'''
id	int	是	商品sku 编号
name	str	是	商品名称
price	decimal	是	单价
default_image_url	str	是	默认图片
comments	int	是	评论量
'''


# POST /browse_histories/ 存储到 redis之中

class UserBrowsingHistoryView(CreateAPIView, ListAPIView):
    """
    用户浏览历史记录 保存到 redis之中！
        1,历史浏览记录两个请求可以封装到一个视图类之中！
        2,get请求是获取数据的请求，需要定义序列化器指定返回字段！
        2,post 请求是存储的过程，在序列化器之中即可实现存储的过程！
    """
    serializer_class = AddUserBrowsingHistorySerializer

    def get(self, request):
        user_id = request.user.id

        redis_conn = get_redis_connection("history")
        # redis列表的获取，(键,位置起始值，结束值！)
        history = redis_conn.lrange("history_%s" % user_id, 0, 4)
        skus = []
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)
        # 序列化对象!传递的事列表！
        # 序列化器可以将列表的数据进行序列化！
        ser_data = SKUSerializer(skus, many=True)
        # 返回给前端是列表，前端处理列表！
        return Response(ser_data.data)


'''
请求参数:
    categroy_id	int	是	类别id（第三级类别）
    page	int	是	页数
    page_size	int	否	每页数量
    ordering	str	是	排序关键字（'create_time', 'price', 'sales'）
'''
'''
返回参数:
    count	int	是	数据总数
    next	url	是	下一页的链接地址
    previous	url	是	上一页的链接地址
    results	sku[]	是	商品sku数据列表
    id	int	否	商品sku 编号
    name	str	否	商品名称
    price	decimal	否	单价
    default_image_url	str	否	默认图片
    comments	int	否	评论量

'''
'''列表页展示！'''


# GET /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    '''
        1,根据商品的种类进行返回数据，因此采用 ListAPIView
        2,重写 get_queryset 方法指定返回的数据字段！
        3,使用排序，根据 ordering 指定的字段(排序是在setting文件之中指定返回类型！)
        4,也可以 ordering_fields = ('create_time', 'price', 'sales')
        5,在settiing之中可以指定返回多少数据，不指定按照url来进行返回！
        5,设置分页返回给前端的字段自动增加上以下字段！
            count	int	是	数据总数
            next	url	是	下一页的链接地址
            previous	url	是	上一页的链接地址
            results	sku[]	是	商品sku数据列表
    '''
    # 以第一个试图使用同样的序列化器！
    serializer_class = SKUSerializer
    # filter_backends = (OrderingFilter,)
    # 指定排序方法！
    # framework会在请求的查询字符串参数中检查是否包含了ordering参数，
    # 如果包含了ordering参数，则按照ordering参数指明的排序字段对数据集进行排序。
    filter_backends = (OrderingFilter,)
    # 指定前端只能按照一下字段进行排序！
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


'''搜索引擎自带的视图！'''


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer
