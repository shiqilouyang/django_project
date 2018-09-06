from django.db import models
from lulu_store.utils.models import BaseModel


# 继承于基类！
class OAuthQQUser(BaseModel):
    """
    QQ登录用户数据
    """
    # CASCADE 级联，删除主表数据时连通一起删除外键表中数据,也就是删除用户也会删除用户对应的此处外键
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    # db_index 表示为此字段创建索引！有助于定位信息，加快寻找速度！
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name
