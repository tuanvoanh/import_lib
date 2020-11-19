from ..sub_serializers.common_serializer import DataImportResponseSerializer
from ..sub_views.base import GenericImportView
from drf_yasg import openapi
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView


class DetailImportView(RetrieveAPIView, GenericImportView):
    response = openapi.Response('response', DataImportResponseSerializer)

    @swagger_auto_schema(operation_description='Retrieve import',responses={status.HTTP_200_OK: response})
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
