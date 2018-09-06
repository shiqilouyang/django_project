'''
    id	int	是	商品sku 编号
name	str	是	商品名称
price	decimal	是	单价
default_image_url	str	是	默认图片
comments	int	是	评论量



'''
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response
# 使用的是搜索模块自带的序列化器！
from drf_haystack.serializers import HaystackSerializer

from goods.models import SKU

# 使用 ModelSerializer 因为与数据库有关！
from goods.search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'comments', 'default_image_url')


# sku_id	int	是	商品sku 编号
class AddUserBrowsingHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField()

    # 在值了 values指的是 sku_id
    def validate_sku_id(self, values):
        try:
            SKU.objects.filter(id=values).all()
        except:
            raise serializers.ValidationError('该商品不存在')

        return values

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']
        # 连接redis 数据库！
        redis_conn = get_redis_connection("history")
        pl = redis_conn.pipeline()

        # 移除已经存在的本商品浏览记录 0 表示移除所有的与 sku_id相同的用户。
        pl.lrem("history_%s" % user_id, 0, sku_id)
        # 添加新的浏览记录
        pl.lpush("history_%s" % user_id, sku_id)
        # 只保存最多5条记录
        pl.ltrim("history_%s" % user_id, 0, 4)

        pl.execute()

        return validated_data


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """

    class Meta:
        # 指定自定义的索引类！
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')
