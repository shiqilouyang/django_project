import base64

import pickle
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response

from goods.models import SKU

'''
    sku_id	int	是	商品sku id
    count	int	是	数量
    selected	bool	否	是否勾选，默认勾选
    
    #在 redis 之中存储！
    sku_id: {
        "count": xxx,  // 数量
        "selected": True  // 是否勾选
    },
    sku_id: {
        "count": xxx,
        "selected": False
    },
'''

'''加入购物车操作！'''


class CartSerializer(serializers.Serializer):
    """
    购物车数据序列化器
    """
    # 商品id
    sku_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(default=True)

    # 字段进行检查！attrs[] 是字典前端传递的值，也就是序列化器的定义的字段！
    def validate(self, attrs):
        try:
            sku_id = SKU.objects.filter(id=attrs['sku_id']).first()
        except:
            raise serializers.ErrorDetail("该商品不存在！")
        if sku_id.stock < attrs['count']:
            raise serializers.ErrorDetail('商品库存不够！')

        return attrs


'''购物车显示！'''
'''
    id	int	是	商品sku id
    count	int	是	数量
    selected	bool	是	是否勾选，默认勾选
    name	str	是	商品名称
    default_image_url	str	是	商品默认图片
    price	decimal	是	商品单价
'''


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField()
    selected = serializers.BooleanField()

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')


'''删除购物车信息！'''


class CartDeleteSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField()

    def validated_sku_id(self, values):
        try:
            sku_id = SKU.objects.filter(id=values).first()
        except:
            raise serializers.ErrorDetail("该商品不存在！")

        return values


class CartSelectAllSerializer(serializers.Serializer):
    selected = serializers.BooleanField(label='全选!')
