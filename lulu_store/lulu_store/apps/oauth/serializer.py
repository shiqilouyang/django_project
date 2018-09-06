import re

from django.conf import settings
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from rest_framework import serializers

# 指定字段！ qq登录后注册需要的字段！
from oauth.models import OAuthQQUser
from users.models import User


class OAuthQQUserSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    # 手机号验证！ 每次验证必须返回数据。
    def validate_mobile(self, data):
        if not re.match(r'^1[3-9]\d{9}$', data):
            raise serializers.ValidationError('手机号不匹配')
        return data

    def validate(self, attrs):
        # 检验token
        # 验证失败，会抛出itsdangerous.BadData异常
        serializer = Serializer(settings.SECRET_KEY, 300)
        try:
            # 解码操作！ 如果没有 token 说明不是通过 qq登陆的！
            openid = serializer.loads(attrs['access_token'])
        except BadData:
            return None
        # 为禁言通过的用户增加字段 openid
        attrs['openid'] = openid
        # 短息验证码验证！
        redis_code = get_redis_connection('verify_codes')
        # 存储到redis之中是byte类型！
        real_sms_code = redis_code.get("sms_%s" % attrs['mobile']).decode()
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')

        if real_sms_code != attrs['sms_code']:
            raise serializers.ValidationError('请输入正确的手机验证码')

        # 用户是否存在，是否在商城进行注册验证！
        try:
            user = User.objects.get(moblie=attrs['mobile'])
        except Exception as e:
            pass
        else:
            # 如果存在就会检验密码！如果密码比对成功九尾用户增加 属性 user
            if user.check_password(attrs['password']):
                attrs['user'] = user
        # 验证密码是否正确！

        return attrs

    # 创建用户操作！
    def create(self, validated_data):
        user = validated_data.get('user', None)
        if not user:
            user = validated_data.get('user', None)
            if not user:
                user = User.objects.create(
                    username=validated_data['mobile'],
                    mobile=validated_data['mobile'],
                    password=validated_data['password']
                )
                user.set_password(validated_data['password'])
                user.save()

        # user用户和openid绑定,当下一次登录的时候直接登录即可！ 参考 views.py 77 行
        qq_user = OAuthQQUser()
        qq_user.user = user
        qq_user.openid = validated_data['openid']

        qq_user.save()

        return user
