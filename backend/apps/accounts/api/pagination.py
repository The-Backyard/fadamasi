from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return a standardized paginated response in the project's format."""
        return Response(
            {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": _("Results retrieved successfully"),
                "data": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )
