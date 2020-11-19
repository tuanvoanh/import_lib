from ..sub_serializers.lib_import_serializer import ProcessDataImportSerializer
from ..sub_serializers.common_serializer import DataImportResponseSerializer
from ..sub_views.base import GenericImportView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins
from rest_framework import status


class ProcessDataImportView(mixins.UpdateModelMixin, GenericImportView):
    serializer_class = ProcessDataImportSerializer
    response = openapi.Response('response', DataImportResponseSerializer)

    @swagger_auto_schema(operation_description='Process import lib', request_body=no_body,
                         responses={status.HTTP_200_OK: response})
    def put(self, request, *args, **kwargs):
        request.data.update({'module': kwargs.get('module')})
        return self.update(request, *args, **kwargs)
