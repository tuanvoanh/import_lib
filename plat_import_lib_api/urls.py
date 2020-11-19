from django.urls import path

from .sub_views.upload import UploadDataImportView
from .sub_views.validate import ValidateDataImportView
from .sub_views.process import ProcessDataImportView
from .sub_views.detail import DetailImportView
from .sub_views.items import ItemImportView
from .sub_views.module import ImportModuleListView
from .sub_views.export import ExportSerializer, ExportSampleView, ExportInvalidView, ExportErrorView

urlpatterns = [
    path(r'<slug:module>', ImportModuleListView.as_view(), name='list-data-import-of-module'),
    path(r'<slug:module>/upload', UploadDataImportView.as_view(), name='upload-data-import-to-module'),
    path(r'<slug:module>/<uuid:import_id>', DetailImportView.as_view(), name='get-data-import-of-module'),
    path(r'<slug:module>/<uuid:import_id>/items', ItemImportView.as_view(), name='items-data-import-of-module'),
    path(r'<slug:module>/<uuid:import_id>/validate', ValidateDataImportView.as_view(),
         name='validate-data-import-of-module'),
    path(r'<slug:module>/<uuid:import_id>/process', ProcessDataImportView.as_view(),
         name='process-data-import-of-module'),
    # export
    path(r'<slug:module>/export/sample', ExportSampleView.as_view(), name='export-sample-data-import-of-module'),
    path(r'<slug:module>/<uuid:import_id>/export/invalid', ExportInvalidView.as_view(),
         name='export-invalid-data-import-of-module'),
    path(r'<slug:module>/<uuid:import_id>/export/error', ExportErrorView.as_view(),
         name='export-error-data-import-of-module'),
    path(r'<slug:module>/<uuid:import_id>/export/all', ExportSerializer.as_view(),
         name='export-all-data-import-of-module')
]
