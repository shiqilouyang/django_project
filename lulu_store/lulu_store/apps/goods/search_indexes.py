from haystack import indexes

from .models import SKU


# 索引类指定搜索引擎根据哪个字段进行索引！
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # text 字段可以自定义增加字段，字段在模板之中！ 位置固定！
    # templates/search/indexes/goods/sku_text.txt
    # document=True表明该字段是主要进行关键字查询的字段
    text = indexes.CharField(document=True, use_template=True)
    # model_attr 表明引用模型类字段！
    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.CharField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集,在此处进行了查询集的过滤操作！"""
        return self.get_model().objects.filter(is_launched=True)
