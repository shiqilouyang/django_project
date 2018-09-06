from django.db import models

# Create your models here.

# 创建行政区三级联动表！

# 行政区三级联动

class Area(models.Model):
    """
    行政区划
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    # 自关联！ blank 允许为空！  null 允许为null(三个值！)
    # on_delete 表示如果删除某信息，那么就将关联本信息的外键设置为 null
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name



