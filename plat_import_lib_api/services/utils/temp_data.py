import logging
from plat_import_lib_api.services.utils.exceptions import InvalidImportDataObjectException
from plat_import_lib_api.models import DataImportTemporary

logger = logging.getLogger(__name__)


class DataTempService:
    @staticmethod
    def get_data_import_temp(lib_import_id: str):
        assert lib_import_id is not None, "Import temp id is not None"
        try:
            temp_info = DataImportTemporary.objects.get(pk=lib_import_id)
        except DataImportTemporary.DoesNotExist:
            logger.error('ResponseDataService.data_import : import temp id {} not found'.format(lib_import_id))
            raise InvalidImportDataObjectException(message='Import Temporary Record not found system')
        return temp_info

    @staticmethod
    def create_import(module: str, file_info: dict = {}, **kwargs) -> DataImportTemporary:
        assert module is not None, "[ImportDataService][create_import] data is not None"
        import_info = dict(module=module, meta=kwargs)
        obj = DataImportTemporary(**import_info, **file_info)
        obj.save()
        return obj

    @staticmethod
    def update_import(lib_import_id: str, **kwargs):
        assert lib_import_id is not None, "Import temp id is not None"
        if kwargs:
            DataImportTemporary.objects.filter(pk=lib_import_id).update(**kwargs)
