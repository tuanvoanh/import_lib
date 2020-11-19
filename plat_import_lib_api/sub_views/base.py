from rest_framework.generics import GenericAPIView, get_object_or_404
from ..sub_serializers.lib_import_serializer import LibImportModelSerializer
from ..models import DataImportTemporary
from ..services.utils.utils import load_lib_module


class GenericImportView(GenericAPIView):
    serializer_class = LibImportModelSerializer
    queryset = DataImportTemporary.objects.all()

    def get_object(self):
        pk = self.kwargs.get('import_id')
        module = self.kwargs.get('module')
        queryset = self.queryset.filter(pk=pk, module=module)
        return get_object_or_404(queryset)

    @property
    def lib_module(self):
        module = self.kwargs['module']
        return load_lib_module(module)

    def validate(self):
        self.lib_module.validate_request_api_view(self.request, *self.args, **self.kwargs)

    def get_permissions(self):
        self.validate()
        self.permission_classes =  self.lib_module.permissions_class
        return super().get_permissions()
