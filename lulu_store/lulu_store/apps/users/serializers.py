import re

from django.conf import settings
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
# 实现邮件的发送！
from celery_tasks.email import tasks
from users.models import User, Address

'''
用户注册类！
    username	str	是	用户名
    password	str	是	密码
    password2	str	是	确认密码
    sms_code	str	是	短信验证码
    mobile	str	是	手机号
    allow	str	是	是否同意用户协议
'''


class CreateUserSerializer(serializers.ModelSerializer):
    '''只需要验证密码手机号与是否同意即可！'''
    # 增加一个返回字段，用来返回记录token的值！
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段
    password2 = serializers.CharField(label='同意', write_only=True)
    sms_code = serializers.CharField(label='手机验证码', max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(label='是否允许', write_only=True)

    class Meta():
        # 为上述字段增加字段验证的功能！
        model = User
        # 指定模型类的那些字段生成！
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 手机号验证！ 每次验证必须返回数据。
    def validate_mobile(self, data):
        if not re.match(r'^1[3-9]\d{9}$', data):
            raise serializers.ValidationError('手机号不匹配')
        return data

    # 是否同意验证！
    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        redis_code = get_redis_connection('verify_codes')
        # 存储到redis之中是byte类型！
        real_sms_code = redis_code.get("sms_%s" % attrs['mobile']).decode()
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')

        if real_sms_code != attrs['sms_code']:
            raise serializers.ValidationError('请输入正确的手机验证码')

        return attrs

    # 创建用户！
    def create(self, validated_data):
        # 移除数据库不存在的属性！
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        # 返回用户对象
        user = super().create(validated_data)

        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()
        # 设置 token 用来保持用户user状态的登录！
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user


'''用户个人中心！'''


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


'''个人中心保存邮箱！'''


class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                # 表明序列化(前端必须发送email)必须带上此字段！
                'required': True
            }
        }

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()

        # 生成 token值 前端发送token 才能确定是否是当前用户发送！
        ser = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
        data = {
            'user_id': instance.id,
            'email': validated_data['email']
        }
        token = ser.dumps(data).decode()

        url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

        # 发送邮件的过程是在保存更新的过程之中！
        tasks.send_emailc_code.delay(validated_data['email'], url)

        return instance


'''收货地址等信息！'''


class UserAddressSerializer(serializers.ModelSerializer):
    # 不使用id 是为了序列化过程返回给前端的数据！
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    # 使用id 是为了反序列化进行验证
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """

    class Meta:
        model = Address
        fields = ('title',)
