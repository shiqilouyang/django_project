from decimal import Decimal
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializer import OrderSettlementSerializer, SaveOrderSerializer


class OrderSettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        conn = get_redis_connection('cart')
        redis_cart = conn.hgetall('cart_%s' % user.id)  # {'sku_id':'数量'}
        cart_selected = conn.smembers('cart_selected_%s' % user.id)  # ('sku_id')
        # 获取所有的商品信息!
        cart = {}
        # 遍历集合构造字典形式!
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])
        list_skus = SKU.objects.filter(id__in=cart.keys())
        freight = Decimal('10.00')

        # 使用
        # dir_responses = {}
        # list = []
        # list_sku = {}
        # for item in list_skus:
        #     list_sku['id'] = item.id
        #     list_sku['name'] = item.name
        #     list_sku['default_image_url'] = item.default_image_url
        #     list_sku['price'] = item.price
        #     list_sku['count'] = str(data[str(item.id).encode()])
        #     list.append(list_sku)
        #     list_sku = {}
        # print(list)
        # 可以序列化器使用字典的,只要序列化器接受属性!
        ser = OrderSettlementSerializer({'skus': list_skus, 'freight': freight})
        return Response(ser.data)


class SaveOrderView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer
