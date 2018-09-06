from rest_framework.pagination import PageNumberPagination


# 需要在 setting之中指定使用自定义的分页类！
class StandardResultsSetPagination(PageNumberPagination):
    # 每页的数量！
    # page_size = 2
    # 指定前端要根据这个字段进行返回！传递6页 page_size=6
    page_size_query_param = 'page_size'
    # 后端最多返回20个页面！
    max_page_size = 20


'''
    # GET /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx


'''
