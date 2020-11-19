import os, logging
from django.conf import settings
from plat_import_lib_api.services.files.csv import CSVImportObject
from plat_import_lib_api.services.files.excel import ExcelImportObject
from ..utils.exceptions import InvalidFormatException
from ...models import DataImportTemporary

logger = logging.getLogger('django')

chunk_size = settings.PLAT_IMPORT_DATA_CHUNK_SIZE if hasattr(settings, 'PLAT_IMPORT_DATA_CHUNK_SIZE') else 2000
PLAT_IMPORT_STORAGE = settings.PLAT_IMPORT_STORAGE if hasattr(settings,
                                                                                'PLAT_IMPORT_STORAGE') else 'google'


class ReaderFileManage(object):

    def __init__(self, lib_import_id: str):
        self.lib_import_id = lib_import_id
        self.lib_import = DataImportTemporary.objects.get(pk=self.lib_import_id)
        self.service = self.load_service()

    def load_service(self):
        file = self.lib_import.temp_file_path
        filename, file_extension = os.path.splitext(file)
        if not file_extension:
            raise InvalidFormatException(message="File not found file_extension")
        args = {
            '.csv': CSVImportObject,
            '.xlsx': ExcelImportObject,
            '.xls': ExcelImportObject,
        }
        instance = args.get(file_extension)(lib_import_id=self.lib_import_id)
        return instance

    def processing(self):
        self.service.process()
