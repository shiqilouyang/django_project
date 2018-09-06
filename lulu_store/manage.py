#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # 指定django文件的加载配置文件
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lulu_store.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    # 读取命令行参数，执行app 代码！  sys.argv 是一个列表，存放用户输入的参数
    execute_from_command_line(sys.argv)
