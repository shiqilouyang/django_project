from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import app


@app.task(name='send_email')
def send_emailc_code(email, verify_url):
    msg = '<p>尊敬的用户您好！</p>' \
          '<p>感谢您使用美多商城。</p>' \
          '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
          '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
    # django 自带的发送邮件的方法！(邮件标题，发送内容,指定发件人，指定收件人列表，以html形式发送地址！)
    send_mail('美多商城验证', '', settings.EMAIL_FROM, [email], html_message=msg)
