from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 1  # Number of items per page

    def get_paginated_response(self, data):
        start_index = (self.page.number - 1) * self.page_size
        end_index = start_index + len(data) - 1

        return Response(data)