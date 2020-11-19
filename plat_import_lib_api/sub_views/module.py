from rest_framework import generics
from plat_import_lib_api.sub_views.base import GenericImportView


class ImportModuleListView(generics.ListAPIView, GenericImportView):

    def get_queryset(self):
        module = self.kwargs.get('module')
        return self.queryset.filter(module=module).order_by('-created')
