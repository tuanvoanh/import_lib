from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from ..sub_serializers.lib_import_serializer import UploadDataImportSerializer
from ..sub_serializers.common_serializer import DataImportResponseSerializer
from ..sub_views.base import GenericImportView


class UploadDataImportView(generics.CreateAPIView, GenericImportView):
    serializer_class = UploadDataImportSerializer
    parser_classes = [FormParser, MultiPartParser]
    response = openapi.Response('response', DataImportResponseSerializer)

    @swagger_auto_schema(operation_description='Upload file import', responses={status.HTTP_200_OK: response})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
