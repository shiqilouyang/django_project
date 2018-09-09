import random

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from django_redis import get_redis_connection
from django.http import HttpResponse

# Create your views here.
from celery_tasks.sms import task as sms_tasks
from lulu_store.libs.captcha.captcha import captcha
from lulu_store.libs.yuntongxun.sms import CCP
from verifications.serializers import ImageCodeCheckSerializer
from . import contents

'''图片验证码！
    前端每次点击都要触发事件请求！ 前端也是拼接的url
    url('^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
'''


# url('^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
# 不需要与数据库交互只是生成验证码，并返回验证码！不需要序列化与反序列化！
class ImagecodeView(APIView):
    '''1,前端发送请求调用get方法！
        2,生成验证码！
        3,保存到redis数据库之中()配置redis数据库！
        4,将图片返回给前端！

    '''

    # request 是封装后的对象！
    def get(self, request, image_code_id):
        # print(type(request)) <class 'rest_framework.request.Request'>
        # 调用第三方生成验证码！
        test, imge = captcha.generate_captcha()
        # 使用第三方库来连接redis
        redis_code = get_redis_connection('verify_codes')
        # 将数据写入到指定的redis之中！(键，保存时间，值)
        redis_code.setex('img_%s' % image_code_id, contents.IMAGE_CODE_REDIS_EXPIRES, test)
        # 图片返回类型，不然老版本的浏览器不识别！
        return HttpResponse(imge, content_type='img/jpg')


'''短信验证！
    由于需要与数据库交互，需要使用序列化与反序列化!
'''



# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """
        1,首先前端发送请求，
        2,序列化器进行序列化字段的验证
        3,取出redis之中的验证码与前端产生的验证码进行对比验证
        4,随机生成手机验证码，
        5，调用第三方向手机发送验证码！
    """
    # 指定序列化器！
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # request.query_params 是将url 上的地址转换成字典形式
        # 获取序列化对象，将前端传数据进行序列化校检！ get_serializer 方法增加三种对象
        ser = self.get_serializer(data=request.query_params)
        # 验证不通过抛出错误！返回400错误。 这里执行序列化器验证(验证的过程就是数据(redis)存储的过程)
        ser.is_valid(raise_exception=True)

        sms_code = "%06d" % random.randint(0, 999999)

        # 获取验证码并且进行验证！
        # redis_code = get_redis_connection('verify_codes')
        # 这里的验证过程交给系列化器！
        # data_fo = redis_code.get('sms_code_test%s' % mobile)
        # if data_fo:
        #     raise Response('你操作太频繁！')

        # redis_code.setex('sms_code%s' % mobile, contents.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_code.setex('sms_code_test%s' %mobile ,contents.SEND_SMS_CODE_INTERVAL)

        # 使用redis管道代替上述的方法！
        redis_code = get_redis_connection('verify_codes')
        pl = redis_code.pipeline()
        # 设置管道，减少一次存储次数！
        pl.setex("sms_%s" % mobile, contents.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 存储另一个字段，是为了时间校检！
        pl.setex("send_flag_%s" % mobile, contents.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 使用第三方平台发送短息！
        sms_code_expires = str(contents.SMS_CODE_REDIS_EXPIRES // 60)
        # ccp = CCP()
        # # [随机数与时间有效期！] 模板
        # ccp.send_template_sms(mobile, [sms_code, sms_code_expires], 1)

        # 使用第三方模块异步来进行发送短信！阻止由于等待造成的程序暂停！
        sms_tasks.send_sms_code.delay(mobile, sms_code, sms_code_expires)
        return Response({'emage': 'ok'})
