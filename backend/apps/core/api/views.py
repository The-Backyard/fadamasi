from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response


@extend_schema(
    responses={200: None},
    description="Root API entry point.",
)
@api_view(["GET"])
def root_api(request):
    return Response({"message": "Fadamasi Backend API Setup"})
