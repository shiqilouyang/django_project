import urllib
from urllib.parse import urlencode, parse_qs
from django.conf import settings
import json
import requests


class OAuthQQ(object):
    """
    QQ认证辅助工具类
    """

    def __init__(self, app_id=None, app_key=None, redirect_uri=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URL
        self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

    def get_qq_login_url(self):
        """
        获取qq登录的网址
        :return: url网址
        """
        params = {
            'response_type': 'code',
            'client_id': self.app_id,
            # 指定重定向地址！
            'redirect_uri': self.redirect_uri,
            'state': self.state,
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_access_token(self, code):
        """
        获取access_token
        :param code: qq提供的code
        :return: access_token
        """
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)

        response = requests.get(url)
        # 返回数据形式 access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
        data = response.text
        data_dict = parse_qs(data)
        # 将查询字符串转换成字典形式！
        # data = parse_qs(data_dict)
        print(type(data_dict))
        # 取出 access_token 的值，是列表的形式！
        access_token = data_dict.get('access_token', None)
        if not access_token:
            raise Exception('aIUSDWIUADWALB')
        return access_token[0]

    def get_openid(self, access_token):
        # 获取用户的 openid
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        # 返回数据形式 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
        response = requests.get(url)
        # 直接返回的是字典类型！
        data = response.text
        # data = parse_qs(data)
        # 先将返回数据切割成json的形式！在转换成字典的形式！
        data = json.loads(data[10:-3])
        # 字典取出 openid 的值！
        data = data.get('openid', None)
        if not data:
            raise Exception('请求失败！')

        return data
