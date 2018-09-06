from django.conf import settings
from django.shortcuts import render
from pymysql import constants
from rest_framework import serializers, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView, \
    DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from itsdangerous import TimedJSONWebSignatureSerializer
from rest_framework.viewsets import GenericViewSet

from users import serializers
# Create your views here.
from users.models import User, Address

from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, UserAddressSerializer

'''用户名查询！'''


# 用户名验证不需要序列化！
# GET usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    def get(self, request, username):
        # 查询姓名，只需要返回姓名，姓名个数即可！
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


'''手机号验证查询！
    只是查询功能，因此继承 APIView 就可以了！
'''


class MobileCountView(APIView):
    # 查询手机号是否存在！
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


'''创建用户，使用第三方扩展状态保持！
    继承了 CreateAPIView 自带 post 函数
    登录的过程之中让 token 值存储到内存之中，退出直接清除内存即可！

'''


class UserView(CreateAPIView):
    """
    用户注册,在使用 CreateAPIView的时候会进行字段验证(序列化时候)！
    """
    serializer_class = CreateUserSerializer

    # 调试时候使用！
    # def post(self, request, *args, **kwargs):
    #     ser = self.get_serializer(data=request.data)
    #     ser.is_valid()
    #     print(ser.errors)
    #     return super().post(request, *args, **kwargs)


'''用户登录在url 之中,在使用第三方rest_framework_jwt 扩展，不需要写退出，已经自带了退出功能！'''

'''个人中心显示！'''


class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = UserDetailSerializer
    # 与认证系统进行同时使用
    permission_classes = [IsAuthenticated]

    # 自定义模型类对象！
    # 如果没有 get_object 那就货获取不到对象！
    # 找不到 pk值，需要自己指定！
    def get_object(self):
        return self.request.user


'''个人中心邮箱注册
    发送是 put 请求，因此 as_view() 寻找 put 方法！
    也就是 继承类之中的 put方法！
    执行更新操作！ request 之中包含 user信息，查询不到 pk值！
    更改 get_object 方法，改变查询对象！
    
'''


class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    # 指明当前模型类数据对象，不知名不能确定模型类数据对象！！
    def get_object(self, *args, **kwargs):
        return self.request.user


'''邮箱链接点击之后进行验证！'''


class VerifyEmailView(APIView):

    def get(self, request):
        # 发送是get 请求，因此使用 query_params 获取参数!
        token = request.query_params.get('token', None)
        if not token:
            return Response({'emssage': '没有携带token信息！'}, status=400)

        de = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
        try:
            data = de.loads(token)
        except:
            return Response({'emssage': '不是此用户！'}, status=400)
        try:
            user_id = data['user_id']
            username = data['email']
        except:
            return Response({'emssage': 'token信息不完整！'}, status=400)

        return Response({'emssage': 'ok'}, status=200)


'''
    添加收货地址，既有post请求，又有get请求
    post 请求是为了写入数据，get请求是为了显示数据

'''


class AddressViewSet(CreateAPIView, ListAPIView, DestroyAPIView, UpdateAPIView):
    serializer_class = UserAddressSerializer
    '''新增收货地址在 CreateAPIView 含有！'''

    # 只要没有删除的数据！返回所有的当前用户所有的收货地址等！
    def get_queryset(self):
        # self.request.user.addresses 不需要使用 object 指定的是 类对象
        return self.request.user.addresses.filter(is_deleted=False)

    # 需要对list重写，因为默认只会返回 serializer.data
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = request.user

        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 10,
            'addresses': serializer.data,
        })

    '''删除用户中心收货地址操作！'''

    def destroy(self, request, *args, **kwargs):
        # 如果有 pk 值那么就会按照pk值进行查找！ 获取的是管理器对象！
        address = self.get_object()
        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    '''设为默认地址！重写put 方法！'''

    def put(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # @action(methods=['put'], detail=True)
    # def title(self, request, pk=None, address_id=None):
    #     """
    #     修改标题
    #     """
    #     address = self.get_object()
    #     serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)


class AddressViewSetDefault(UpdateAPIView):
    serializer_class = UserAddressSerializer

    # 获取查询集合
    def get_queryset(self):
        # self.request.user.addresses 不需要使用 object 指定的是类对象
        return self.request.user.addresses.filter(is_deleted=False)

    def put(self, request, *args, **kwargs):
        # 从 get_queryset 之中获取对象！
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
