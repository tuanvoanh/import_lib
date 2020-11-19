import json

from plat_import_lib_api.models import DataImportTemporary
from plat_import_lib_api.services.utils.utils import load_lib_module


class LibImportObject:
    def __init__(self, lib_import_id: str, **kwargs):
        self.lib_import_id = lib_import_id
        self.lib_import = DataImportTemporary.objects.get(pk=self.lib_import_id)
        self.kwargs = kwargs
        #
        self.file_path = self.lib_import.temp_file_path

        self.lib_module = load_lib_module(self.lib_import.module)

        self.serializer = self.lib_module.serializer_class

        self.info_import_file = self.lib_import.info_import_file

        self.map_config = self.info_import_file.get('map_cols_to_module', [])

        self.data_import_file = json.loads(self.lib_import.json_data)

        # validate job type action
        self.validate()

    def validate(self):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError
