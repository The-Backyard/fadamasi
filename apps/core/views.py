from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def root_api(request):
    return Response({"message": "Fadamasi Backend API Setup"})
