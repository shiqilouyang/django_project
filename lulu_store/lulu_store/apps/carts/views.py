import base64
import pickle
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from pymysql import constants
from rest_framework import status

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from carts.serializer import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelectAllSerializer

# POST /cart/
from goods.models import SKU


class CartView(GenericAPIView):
    """
    购物车
    """

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        """
        pass

    serializer_class = CartSerializer

    # 加入购物车
    def post(self, request):
        # 进行数据验证
        ser = self.get_serializer(data=request.data)
        ser.is_valid()
        # 从序列化器之中获取数据
        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']
        try:
            user = request.user
        except:
            user = None
        if user:
            # 用户已经登录
            # 建立连接
            conn = get_redis_connection('cart')
            pl = conn.pipeline()
            # 先写数量关系  哈希类型(键，{字段，个数})
            pl.hincrby('cart_%s' % user.id, sku_id, count)

            # 写入是否选中状态 (键，商品id)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(ser.data)
        else:
            # 用户未登录，在cookie中保存　构造以下保存形式！
            # {
            #     1001(sku_id): { "count": 10, "selected": true},
            #     ...
            # }
            # 先判断有没有写入过cookies数据
            cart = request.COOKIES.get('cart')
            if cart:
                # 说明以前写入过
                # 解密
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            # 判断当前sku是否写入过
            '''
             sku_id: {
                    "count": xxx,  // 数量
                    "selected": True  // 是否勾选
                },

            '''
            sku = cart.get(sku_id, None)
            # sku 是字典类型！
            if sku:
                # 前端传递的数量加上，再次cookie中的数量，组成最终的数量
                count += int(sku['count'])
            # 组建新的数据字典
            cart[sku_id] = {
                "count": count,
                "selected": selected
            }

            # 反回数据
            # 加密 将字典数据编码为byte类型的数据！保证cookie之中存放的是 byte类型的数据！
            cookies_cart = base64.b64encode(pickle.dumps(cart)).decode()

            response = Response(ser.data)

            response.set_cookie('cart', cookies_cart, 60 * 60 * 24)

            return response

    # 购物车信息显示！
    def get(self, request):
        '''
            1,验证用户是否登录，登录在 redis之中取值，没有登录在　cookies之中取值！
            2,redis之中取值，取出的值与 response数据进行拼接！cookie 同redis一样！
            3,将查询集对象置序列化器之中！
            4,返回数据！
        '''
        # get 请求没有使用到序列化的过程！
        try:
            # 验证有没有用户登录， jwt 也会再次进行检查操作！因此需要进行捕获异常操作！
            user = request.user
        except:
            user = None
        if user:
            '''用户登录需要从redis之取出值！'''
            conn = get_redis_connection('cart')
            pl = conn.pipeline()
            # 获取到的是字典的形式！
            # 返回的是byte字典类型！
            count_cart = pl.hgetall('cart_%s' % user.id)
            redis_cart_selected = pl.smembers('cart_selected_%s' % user.id)
            data = pl.execute()
            # data =  [{b'14': b'2', b'16': b'1', b'10': b'1'}, {b'14', b'10', b'16'}]
            dir_data = {}
            for sku_id, count in data[0].items():
                # {
                #     1001(sku_id): { "count": 10, "selected": true},
                #     ...
                # }
                # 组建在字典的形式传递给前端！
                dir_data[sku_id.decode()] = {
                    'count': count.decode(),
                    'selected': sku_id.decode() in data[1]
                }
                print(dir_data)
        else:
            # 需要 cookies 之中取出值！
            cook = request.COOKIES.get('cart')
            if cook:
                # 将 cookies 解码成 字典类型数据！
                dir_data = pickle.loads(base64.b64decode(cook.encode()))
            else:
                dir_data = {}
            sku_data = SKU.objects.filter(id__in=dir_data.keys())
            for sku in sku_data:
                sku.count = dir_data[sku.id]['count']
                sku.selected = dir_data[sku.id]['selected']
                # 使用列表传递或者使用字典传递都可以!返回多个值而已!
            ser = CartSKUSerializer(data=sku_data, many=True)
            ser.is_valid()
            return Response(ser.data)

        sku_data = SKU.objects.filter(id__in=dir_data.keys())

        # 构造前端需要的数据显示！
        for sku in sku_data:
            # 必须转换字符串！因为sku_id.decode()为字符串类型！
            sku.count = dir_data[str(sku.id)]['count']
            sku.selected = dir_data[str(sku.id)]['selected']
        ser = CartSKUSerializer(data=sku_data, many=True)
        ser.is_valid()
        return Response(ser.data)

    # 更改字段操作，知识序列化的过程
    def put(self, request):
        '''
            sku_id	int	是	商品sku id
            count	int	是	数量
            selected	bool	否	是否勾选，默认勾选
        '''
        ser = self.get_serializer(data=request.data)
        ser.is_valid()
        # 获取数据
        sku_id = ser.validated_data['sku_id']
        count = ser.validated_data['count']
        selected = ser.validated_data['selected']

        try:
            # 验证有没有用户登录， jwt 也会再次进行检查操作！因此需要进行捕获异常操作！
            user = request.user
        except:
            user = None
        if user:
            '''用户登录需要从redis之取出值！'''
            conn = get_redis_connection('cart')
            pl = conn.pipeline()
            # 先写数量关系  哈希类型(键，{字段，个数})
            pl.hset('cart_%s' % user.id, sku_id, count)

            # 写入是否选中状态 (键，商品id)
            if selected:
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(ser.data)
        else:
            # 用户未登录，在cookie中保存　构造以下保存形式！
            # {
            #     1001(sku_id): { "count": 10, "selected": true},
            #     ...
            # }
            # 先判断有没有写入过cookies数据
            cart = request.COOKIES.get('cart')
            if cart:
                # 说明以前写入过
                # 解密
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            # 判断当前sku是否写入过
            '''
             sku_id: {
                    "count": xxx,  // 数量
                    "selected": True  // 是否勾选
                },

            '''
            # 构造返回给前端的数据！
            cart[sku_id] = {
                "count": count,
                "selected": selected
            }

            # 反回数据
            # 加密 将字典数据编码为byte类型的数据！
            cookies_cart = base64.b64encode(pickle.dumps(cart)).decode()

            response = Response(ser.data)

            response.set_cookie('cart', cookies_cart, 60 * 60 * 24)

            return response

    # 删除购物车信息！
    def delete(self, request):
        '''
            参数	类型	是否必须	说明
            sku_id	int	是	商品sku id
        '''
        # 将数据传入是为了进行数据验证使用的！
        ser = CartDeleteSerializer(data=request.data)
        ser.is_valid()
        # 获取数据
        sku_id = ser.validated_data['sku_id']
        try:
            # 验证有没有用户登录， jwt 也会再次进行检查操作！因此需要进行捕获异常操作！
            user = request.user
        except:
            user = None
        if user:
            '''用户登录需要从redis之取出值！'''
            conn = get_redis_connection('cart')
            pl = conn.pipeline()
            # 先写数量关系  哈希类型(键，{字段，个数})
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(ser.data)

        else:
            # 用户未登录，在cookie中保存
            response = Response(status=status.HTTP_204_NO_CONTENT)
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart = request.COOKIES.get('cart')
            if cart:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                if sku_id in cart:
                    # 根据id删除选中的数据！
                    del cart[sku_id]
                    cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                    # 设置购物车的cookie
                    # 需要设置有效期，否则是临时cookie
                    response.set_cookie('cart', cookie_cart, max_age=60 * 60 * 24)
            return response


class CartSelectAllView(GenericAPIView):
    '''
    前端发送请求为post请求!
    selected	bool	是	是否全选，true表示全选，false表示取消全选
    '''
    serializer_class = CartSelectAllSerializer

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        """
        pass

    def put(self, request):
        # 将数据进行序列化器进行检验！
        ser = CartSelectAllSerializer(data=request.data)
        ser.is_valid()
        # 获取序列化器中的数据
        selected = ser.validated_data['selected']
        try:
            # 验证有没有用户登录， jwt 也会再次进行检查操作！因此需要进行捕获异常操作！
            user = request.user
        except:
            user = None

        if user:
            redis_conn = get_redis_connection('cart')
            cart = redis_conn.hgetall('cart_%s' % user.id)
            sku_id_list = cart.keys()
            print(sku_id_list)
            if selected:
                # 全选
                redis_conn.sadd('cart_selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                redis_conn.srem('cart_selected_%s' % user.id, *sku_id_list)

            return Response({'message': 'OK'})
        else:
            # cookie
            cart = request.COOKIES.get('cart')

            response = Response({'message': 'OK'})

            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                # 设置购物车的cookie
                # 需要设置有效期，否则是临时cookie
                response.set_cookie('cart', cookie_cart, max_age=60 * 60 * 24)

            return response
