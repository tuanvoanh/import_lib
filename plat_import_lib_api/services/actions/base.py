import json

from ..objects.lib_import import LibImportObject
from ...models import DataImportTemporary, VALIDATING, VALIDATED, PROCESSING, PROCESSED
from ..utils.utils import divide_chunks
from ...static_variable.action import UPLOAD_ACTION, VALIDATE_ACTION, PROCESS_ACTION
from ...static_variable.config import PLAT_IMPORT_DATA_CHUNK_SIZE


class LibBaseAction(LibImportObject):
    JOB_ACTION = None

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        # config for process
        self.progress = 0  # percent process action
        self.chunks_list_process = []
        self.total_success = 0
        self.total_errors = 0

    def validate(self):
        if not self.JOB_ACTION:
            raise NotImplementedError

    def process(self):
        raise NotImplementedError

    @property
    def status_action(self):
        if self.JOB_ACTION == UPLOAD_ACTION:
            if self.progress < 100:
                return VALIDATING
            return VALIDATED
        if self.JOB_ACTION == VALIDATE_ACTION:
            if self.progress < 100:
                return VALIDATING
            return VALIDATED

        if self.JOB_ACTION == PROCESS_ACTION:
            if self.progress < 100:
                return PROCESSING
            return PROCESSED

    def reset_summary(self):
        if self.JOB_ACTION == VALIDATE_ACTION:
            self.info_import_file['summary']['total_errors']['count'] = 0
            self.info_import_file['summary']['total_errors']['raws_index'] = []
            #
            self.info_import_file['summary']['total_success']['count'] = 0
            self.info_import_file['summary']['total_success']['raws_index'] = []
        if self.JOB_ACTION == PROCESS_ACTION:
            self.info_import_file['summary']['total_complete']['count'] = 0
            self.info_import_file['summary']['total_complete']['raws_index'] = []

    def validate_total_type(self, total_type):
        assert total_type in ['total_errors', 'total_success', 'total_complete'], "Total type add summary not correct"

    def add_count_process(self, total_type: str):
        self.validate_total_type(total_type)
        self.info_import_file['summary'][total_type]['count'] += 1

    def add_raw_number_process(self, total_type: str, raw_index: any):
        self.validate_total_type(total_type)
        self.info_import_file['summary'][total_type]['raws_index'].append(raw_index)

    @property
    def chunks_raws_file(self):
        return list(divide_chunks(self.data_import_file, PLAT_IMPORT_DATA_CHUNK_SIZE))

    @property
    def total_rows_data(self):
        return len(self.data_import_file)

    @property
    def total_chunk_records(self):
        return len(self.chunks_list_process)

    def update_to_lib_import(self, rows_file: list = [], **kwargs):
        self.progress = round((self.total_chunk_records / self.total_rows_data * 100), 2)
        data = {
            'status': self.status_action,
            'progress': self.progress,
            'total_process': self.total_chunk_records,
            'info_import_file': self.info_import_file
        }
        if len(rows_file) > 0:
            data['json_data_last_cache'] = json.dumps(rows_file)
        data = {**data, **kwargs}
        print(f"status : {data['status']}, progress : {data['progress']}")
        DataImportTemporary.objects.filter(pk=self.lib_import_id).update(**data)

    def validate_data_request(self, data_request: dict, **kwargs):
        serializer = self.serializer(data=data_request)
        serializer.is_valid()
        errors = serializer.errors
        validated_data = serializer.validated_data
        return validated_data, errors
