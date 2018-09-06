#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from rest_framework.generics import GenericAPIView
# 第三方模块生成 token 值
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from oauth.models import OAuthQQUser
from oauth.serializer import OAuthQQUserSerializer
from oauth.utils import OAuthQQ
from django.conf import settings

'''1，使用qq登录，并且跳转到登录界面,登录成功之后，qq服务器会返回一个 code 参数值！'''


class QQAuthURLView(APIView):
    """
    获取QQ登录的url
    """

    def get(self, request):
        state = request.query_params.get('state')

        # 生成qq对象调用方法
        oauth = OAuthQQ(state=state)

        # 获取qq登录url

        # 为请求加上必须的信息！ 返回的是 qq提供的地址！
        login_url = oauth.get_qq_login_url()

        return Response({'login_url': login_url})


'''2,前端获取到携带QQ提供的code参数，用于获取用户信息使用，
我们需要将这个code参数发送给后端，
在后端中使用code参数向QQ请求用户的身份信息，并查询与该QQ用户绑定的用户。
'''


class QQAuthuserView(GenericAPIView):
    # 指定序列化器！
    serializer_class = OAuthQQUserSerializer

    def get(self, request):
        # 取出前端获取到的 code 值
        code = request.query_params.get('code', None)
        oauth = OAuthQQ()
        try:
            # 3, 通过 code 值与urllib 向服务器获取 access_token的值
            access_token = oauth.get_access_token(code)
            # 4, 根据 access_token 的值，再次使用工具类 urllib 发送 获取 openid的值！
            openid = oauth.get_openid(access_token)
        except Exception as e:
            return Response({'message': e}, status=400)

        try:
            # 查询qq用户是否q用户是否注册商城！
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except Exception as e:
            '''如果 qq没有注册，那么就要跳转到注册次商城注册页面！ 
                为此页面设置，tonken 值,只让qq验证用户跳转到此页面！
            '''
            # 使用第三方模块itsdangerous设置 token 值
            # serializer = Serializer(秘钥, 有效期秒)
            serializer = Serializer(settings.SECRET_KEY, 300)
            # serializer.dumps(数据), 返回bytes类型
            token = serializer.dumps({'mobile': '18512345678'})
            token = token.decode()
            # 返回给前端，前端跳转的注册页面
            return Response({
                'access_token': token
            })
        else:
            # 如果查询到qq存在的用户在商城之中注册！那么就登录进去！
            user = qq_user.user
            # 设置 token 用来保持用户user状态的登录！
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user.token = token
        # 前端将返回到的信息存储到本地！以后的检验过程，就是比对 token 的过程！
        return Response(
            {
                "token": token,
                "username": user.username,
                "user_id": user.id
            }
        )

    '''用户注册！'''

    def post(self, request):
        # 序列化操作！
        ser = self.get_serializer(data=request.data)
        ser.is_valid()
        # 如果用户没有登录就会创建用户！
        user = ser.save()

        # 生成JWTToken
        # 为登录过得用户写入token 值
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response(
            {
                'token': token,
                'username': user.username,
                'user_id': user.id
            }
        )
