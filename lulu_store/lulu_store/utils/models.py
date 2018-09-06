from django.db import models


# 创建模型类的基类！
class BaseModel(models.Model):
    """为模型类补充字段"""
    # auto_now_add 第一次保存会保存当前时间！可以手动更改
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # auto_now 会自动保存当前时间，在执行 save之后
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True  # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表
