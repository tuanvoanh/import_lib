from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.controllers.module import ModuleImportService
from ..sub_views.base import GenericImportView
from ..sub_serializers.lib_import_serializer import ExportDataImportSerializer, ExportSampleSerializer


class ExportSampleView(APIView):
    permission_classes = (AllowAny,)
    export_response = openapi.Response('response', ExportSampleSerializer)

    @swagger_auto_schema(operation_description='Export data simple', request_body=no_body,
                         responses={status.HTTP_200_OK: export_response})
    def get(self, request, *args, **kwargs):
        module = kwargs.get('module')
        module_import = ModuleImportService(name=module).load_module()
        # temp data
        url = module_import.template
        return Response(data={'file_uri': url}, status=status.HTTP_200_OK)


class ExportSerializer(generics.RetrieveAPIView, GenericImportView):
    serializer_class = ExportDataImportSerializer
    type_export = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'type_filter': self.type_export})
        return context


class ExportInvalidView(ExportSerializer):
    type_export = 'invalid'


class ExportErrorView(ExportSerializer):
    type_export = 'errors'
