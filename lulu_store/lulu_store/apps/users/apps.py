from django.apps import AppConfig


'''
    在每个应用目录中都包含了apps.py文件，用于保存该应用的相关信息。

'''


class UserConfig(AppConfig):
    # name 属性表示这个配置类是加载到哪个应用的，每个配置类必须包含此属性，默认自动生成。
    name = 'users'
    # verbose_name 属性用于设置该应用的直观可读的名字，此名字在Django提供的Admin管理站点中会显示
    # verbose_name = '用户管理'

