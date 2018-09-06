#!/usr/bin/env python

"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./regenerate_index_html.py


"""
import sys

# 设置导包路径，如果不设置那么就要绝对路径导包！
sys.path.insert(0, '../')
sys.path.insert(0, '../lulu_store/apps')

import os

# 将django 配置文件导入到本地脚本文件之中！
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lulu_store.settings.dev'

# 让django进行初始化设置
import django

django.setup()

from contents.crons import generate_static_index_html

if __name__ == '__main__':
    generate_static_index_html()

'''
为了方便开发，随时生成静态化首页，我们可以在scripts中新建静态化首页的脚本

'''
