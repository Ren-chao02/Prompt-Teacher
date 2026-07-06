from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class SafePageNumberPagination(PageNumberPagination):
    """分页器：页码超出范围时返回空数据而非 404"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        self.request = request  # get_next_link/get_previous_link 依赖此属性

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            page_number = 1

        if page_number > paginator.num_pages:
            # 超出范围：返回空列表，不抛 404
            self.page = None
            return []

        self.page = paginator.page(page_number)
        return list(self.page)

    def get_paginated_response(self, data):
        """统一分页响应格式"""
        if self.page is None:
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            })
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
