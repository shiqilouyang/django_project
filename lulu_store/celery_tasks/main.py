from celery import Celery

# 为celery使用django配置文件进行设置
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    # 指定配置文件的位置！
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lulu_store.settings.dev'

# 创建celery应用
app = Celery('meiduo')

# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自动注册celery任务, 注册邮箱与手机号发送任务！
app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])

'''
    启动异步任务！
    celery -A celery_tasks.main worker -l info

'''
