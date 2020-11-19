import copy
import itertools
import json
import logging
import time
import maya
from django.utils import timezone

from .base import LibBaseAction
from ...models import DataImportTemporary
from ...static_variable.action import PROCESS_ACTION

logger = logging.getLogger(__name__)


class LibProcessAction(LibBaseAction):
    JOB_ACTION = PROCESS_ACTION

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        self.data_import_file = json.loads(self.lib_import.json_data_last_cache)

        self.serializer = self.lib_module.serializer_class

        self.start_time = time.time()

        self.total_success = 0
        self.total_errors = 0

        # bulk process

        self.bulk_config = {}

        self.init_bulk_config()

    def init_bulk_config(self):
        self.bulk_config = {
            'insert': [],
            'update': []
        }

    def process_bulk(self):
        inserts = self.bulk_config['insert']
        updates = self.bulk_config['update']
        self.lib_module.bulk_process(self.lib_import_id, inserts, updates)
        self.init_bulk_config()

    @property
    def total_raws(self):
        return self.info_import_file['summary']['total']

    def process(self):
        #
        chunks_remain = copy.deepcopy(self.chunks_raws_file)

        self.reset_summary()
        self.update_to_lib_import()

        for chunk in self.chunks_raws_file:
            del chunks_remain[0]
            logger.info("process chunk size: {}".format(len(chunk)))

            self._process_raws(rows=chunk)

            self.process_bulk()

            total_remain_record = list(itertools.chain.from_iterable(copy.deepcopy(chunks_remain)))
            raws_file = self.chunks_list_process + total_remain_record

            # update done
            self.update_to_lib_import(raws_file)

    def _process_raws(self, rows: list = []):
        for row in rows:
            if not row['_meta']['valid']:
                continue
            self._handler_process_row(row=row)
        self.chunks_list_process += rows

    def _handler_process_row(self, row: dict):
        data_request = {}

        # serializer
        target_cols = self.lib_module.target_cols
        map_config_dict = {item['target_col']: item['upload_col'] for item in self.map_config}

        for item in target_cols:
            _upload_col_name = map_config_dict.get(item['name'], None)
            if not _upload_col_name:
                continue
            _upload_col_val = row.get(_upload_col_name, None)
            if _upload_col_val is None:
                continue
            if item['type'] == 'datetime':
                try:
                    date_time_parsed = maya.parse(_upload_col_val)
                    _upload_col_val = date_time_parsed.datetime().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
                except Exception as ex:
                    pass
            data_request[item['name']] = _upload_col_val

        validated_data = self.validate_data_request(data_request, row)

        validated_data = self.lib_module.handler_validated_data(self.lib_import_id, validated_data,
                                                                **self.lib_import.meta)
        obj, created = self.lib_module.make_instance(self.lib_import_id, validated_data)
        self.add_obj_to_bulk(obj, created)

    def add_obj_to_bulk(self, obj: any, created: bool):
        if created:
            self.bulk_config['insert'].append(obj)
        else:
            self.bulk_config['update'].append(obj)

    def validate_data_request(self, data_request: dict, row: dict = {}, **kwargs):
        if not row:
            raise NotImplementedError
        validated_data, errors = super().validate_data_request(data_request)
        if len(errors) > 0:
            _error_update = []
            for key in errors:
                item = {
                    'code': key,
                    'message': errors[key]
                }
                _error_update.append(item)
            row['_meta']['complete'] = False
            row['_meta']['processing_errors'] = _error_update
        else:
            row['_meta']['complete'] = True
            row['_meta']['processing_errors'] = []
            self.add_count_process('total_complete')
            self.add_raw_number_process('total_complete', row['_meta']['number'])
        #
        return validated_data
