from ..sub_serializers.lib_import_serializer import ItemsDataImportSerializer
from ..sub_serializers.common_serializer import ItemsListSerializer
from ..sub_views.base import GenericImportView
from drf_yasg import openapi
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView


class ItemImportView(RetrieveAPIView, GenericImportView):
    serializer_class = ItemsDataImportSerializer

    type = openapi.Parameter('type', in_=openapi.IN_QUERY,
                             description="""Search type valid , invalid ...""",
                             type=openapi.TYPE_STRING)
    key = openapi.Parameter('key', in_=openapi.IN_QUERY,
                            description="""Search key value""",
                            type=openapi.TYPE_STRING)
    search = openapi.Parameter('s', in_=openapi.IN_QUERY,
                               description="""Search value""",
                               type=openapi.TYPE_STRING)

    page = openapi.Parameter('page', in_=openapi.IN_QUERY,
                             description="""Page""",
                             type=openapi.TYPE_INTEGER)

    limit = openapi.Parameter('limit', in_=openapi.IN_QUERY,
                              description="""Limit""",
                              type=openapi.TYPE_INTEGER)

    response = openapi.Response('response', ItemsListSerializer)

    @swagger_auto_schema(operation_description='Get import detail', manual_parameters=[type, search, page, limit],
                         responses={status.HTTP_200_OK: response})
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
