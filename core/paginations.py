from rest_framework.pagination import PageNumberPagination


class BasePageNumberPagination(PageNumberPagination):
    max_page_size = 300
    page_size = 30
    page_size_query_param = "page_size"
