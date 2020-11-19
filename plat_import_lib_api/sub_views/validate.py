from .base import GenericImportView
from ..sub_serializers.lib_import_serializer import ValidateDataImportSerializer
from ..sub_serializers.common_serializer import DataImportResponseSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import status


class ValidateDataImportView(mixins.UpdateModelMixin, GenericImportView):
    serializer_class = ValidateDataImportSerializer
    response = openapi.Response('response', DataImportResponseSerializer)

    @swagger_auto_schema(operation_description='Validate file import', responses={status.HTTP_200_OK: response})
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
