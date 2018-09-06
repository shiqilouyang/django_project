from rest_framework import serializers

from area.models import Area


class AreaSerializer(serializers.ModelSerializer):
    """
    行政区划信息序列化器
    """

    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializer(serializers.ModelSerializer):
    """
    子行政区划信息序列化器
    """
    # read_only 不能进行反序列化操作！
    # 通过一个序列化器来返回另一个序列化器的信息！
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')
