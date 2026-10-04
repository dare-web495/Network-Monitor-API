from rest_framework.pagination import LimitOffsetPagination

class SafeLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100 