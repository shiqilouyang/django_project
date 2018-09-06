from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response

'''
mobile	str	是	手机号
image_code_id	uuid字符串	是	图片验证码编号
text	str	是	用户输入的图片验证码

'''


class ImageCodeCheckSerializer(serializers.Serializer):
    # 以下两个字段可以不是模型类中的必须有的字段！serializers 是独立于数据库之外的存在！
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    # 在这里执行序列暖气验证！
    def validate(self, attrs):
        #django-redis提供了get_redis_connection的方法，
        # 通过调用get_redis_connection方法传递redis的配置名称可获取到redis的连接对象，
        # 通过redis连接对象可以执行redis命令。
        redis_code = get_redis_connection('verify_codes')
        real_test = redis_code.get('img_%s' % attrs['image_code_id'])
        if not real_test:
            raise serializers.ValidationError('无效的验证码！')
            # 每次获取后，要删除验证码！
        redis_code.delete('img_%s' % attrs['image_code_id'])

        if real_test.decode().lower() != attrs['text'].lower():
            raise serializers.ValidationError('验证码错误！！')

        # 由视图接受前端数据，view 通过get_serializer 方法将数据传递给序列化器！
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_code.get("send_flag_%s" % mobile)
        # 判断是否在60s内
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')

        return attrs
