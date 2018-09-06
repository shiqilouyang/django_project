import re
from django.contrib.auth.backends import ModelBackend

# 自定义返回前端数据！ user 是指用户对象！ token 是指！加密的随机值！
from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


'''自定义认证后端,提供手机登录！'''


class UsernameMobileAuthBackend(ModelBackend):
    # 接受前端传递参数！，并定义参数类型校验！
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if re.match(r'^1[3-9]\d{9}$', username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)

        except:
            user = None

        if user is not None and user.check_password(password):
            return user
