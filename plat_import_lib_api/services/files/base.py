import json, logging, time, maya

from dateutil.parser import parse
from django.conf import settings
from django.core.files.storage import default_storage
from plat_import_lib_api.services.files.utils import suggest_upload_column_to_target_column
from plat_import_lib_api.models import STATUS_CHOICE, DataImportTemporary
from .storage import StorageFileManage, STORAGE_DOWNLOAD_ACTION
from ..objects.lib_import import LibImportObject
from ..utils.exceptions import InvalidFormatException
from ...static_variable.config import PLAT_IMPORT_STORAGE

logger = logging.getLogger('django')


class FileImportInterface(LibImportObject):

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id)

        #
        self.header = []
        self.total_progress = 0
        self.total = 0
        self.num_row_empty = 0
        self.num_row = 1
        self.start_time = None

        self.load_workbook()

        #
        #
        self.map_upload_to_target_cols = {}
        #
        self.config_cols_key = {item['name']: item for item in self.lib_module.target_cols}

    def process_row(self, *args, **kwargs):
        raise NotImplemented

    def validate(self):
        self.load_file_remote_service()
        # validate file is not None or file not exists
        path_storage = default_storage.generate_filename(self.file_path)
        if not default_storage.exists(path_storage):
            raise InvalidFormatException(message="File not exist in system for uploader")

    def load_file_remote_service(self):
        if PLAT_IMPORT_STORAGE == 'google':
            try:
                if not self.file_path:
                    raise InvalidFormatException(message='File upload is not empty')
                file_manager = StorageFileManage(file_path=self.file_path, module=self.lib_import.module,
                                                 action=STORAGE_DOWNLOAD_ACTION)
                file_path = file_manager.process()
                self.update_import_file_uploader(temp_file_path=file_path)
                self.file_path = file_path
            except Exception as ex:
                print(ex)
                pass

    def get_header(self):
        pass

    def get_total(self):
        pass

    def init_meta(self):
        _meta = {
            'number': self.num_row,  # row number
            'valid': False,  # false if invalid
            'type': 'created',
            'complete': False,  # false if invalid or processed with error
            'validation_errors': [],  # list of error to display
            'processing_errors': []
        }
        return _meta

    def init_info_import_file(self):
        self.get_header()
        self.get_total()
        map_config = []
        # default map by row index, will using regex pattern from config for map
        map_config = suggest_upload_column_to_target_column(self.lib_module.target_cols, self.header)
        self.info_import_file = {
            'cols_file': self.header,
            'map_cols_to_module': map_config,
            'hash_map_config': None,
            'summary': {
                'total': self.total,
                'total_success': {'count': 0, 'raws_index': []},
                'total_errors': {'count': 0, 'raws_index': []},
                'total_complete': {'count': 0, 'raws_index': []}
            }
        }
        # update import uploader
        self.update_import_file_uploader(info_import_file=self.info_import_file)

    def handle_final_upload(self):
        if self.num_row_empty > 0:
            # exclude row empty
            self.info_import_file['summary']['total'] -= self.num_row_empty
            self.update_import_file_uploader(info_import_file=self.info_import_file)

    def update_process_upload(self, raws_file):
        logger.info("total process file : {}".format(self.total_progress))
        progress = int(self.total_progress / self.total * 100)
        status = STATUS_CHOICE[1][0] if progress == 100 else STATUS_CHOICE[0][0]
        #
        time_exc = str(time.time() - self.start_time) if progress == 100 else None
        #
        json_data = json.dumps(raws_file)
        update = dict(status=status, progress=progress, total_process=self.total_progress, time_exc=time_exc,
                      json_data=json_data, json_data_last_cache=json_data)
        # update info uploader chunk to records db
        self.update_import_file_uploader(**update)

    def is_date(self, value):
        """
        Check value is datetime format
        :param value:
        :return:
        """
        try:
            if not isinstance(value, str):
                return False
            parse(value)
            maya.parse(value)
            return True
        except ValueError:
            return False

    # def round_currency(self, value):
    #     next_cent = settings.PLAT_IMPORT_ROUND_UP if hasattr(settings,
    #                                                          'PLAT_IMPORT_ROUND_UP') else 0
    #     _round = round(value, 2)
    #     _temp = _round - value
    #     if _temp >= 0:
    #         value = _round
    #     else:
    #         value = round(_round + next_cent, 2)
    #     return value

    def load_workbook(self):
        raise NotImplemented

    def get_info(self):
        raise NotImplemented

    def update_import_file_uploader(self, **kwargs):
        DataImportTemporary.objects.filter(pk=self.lib_import_id).update(**kwargs)
