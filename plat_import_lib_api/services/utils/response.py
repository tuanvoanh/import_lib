import json
import logging
import re

from django.core.paginator import Paginator

from .utils import normalize_map_config
from ..objects.lib_import import LibImportObject
from django.http import FileResponse
import mimetypes
import os
from wsgiref.util import FileWrapper

logger = logging.getLogger(__name__)


class ResponseDataService(LibImportObject):

    def __init__(self, lib_import_id: str, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        self.map_cols_obj = {_item['target_col']: _item['upload_col'] for _item in self.map_config}

    def validate(self):
        pass

    def process(self):
        pass

    @property
    def data_import(self):
        data = {
            'id': str(self.lib_import.pk),
            'name': self.lib_module.name,
            'label': self.lib_module.label,
            'meta': self.lib_import.meta,
            'status': self.lib_import.status,
            'progress': self.lib_import.progress,
            'columns': self.lib_module.target_cols,
            'summary': {
                'total': self.info_import_file.get('summary', {}).get('total', {}),
                'valid': self.info_import_file.get('summary', {}).get('total_success', {}).get('count', 0),
                'completed': self.info_import_file.get('summary', {}).get('total_complete', {}).get('count', 0),
            },
            'upload_columns': self.info_import_file.get('cols_file', []),
            'column_mapping': self.map_config,
            'created': self.lib_import.created,
            'updated': self.lib_import.modified,
            'validation_started': self.lib_import.validation_started,
            'validation_completed': self.lib_import.validation_completed,
            'process_started': self.lib_import.process_started,
            'process_completed': self.lib_import.process_completed
        }
        data = self.lib_module.handler_response_detail(data)
        return data

    @property
    def summary_import(self):
        _sum = self.info_import_file.get('summary')
        sm = {
            'total': _sum['total'],
            'total_success': _sum['total_success']['count'],
            'total_errors': _sum['total_errors']['count']
        }
        return sm

    def items_import(self, filters: dict = {}, page: int = 1, limit: int = 20):

        list_objs = self.filter_raws_data_temp(filters=filters)
        #
        p = Paginator(object_list=list_objs, per_page=limit)
        try:
            page_current = p.page(number=page)
            items = self.normalize_data_rows_file(raws_file=page_current.object_list)
        except Exception as ex:
            logger.error(f'[items_import]: {ex}')
            items = []
        data = dict(
            total=p.count,
            page_current=page,
            page_count=p.num_pages if items else 0,
            page_size=limit,
            items=items
        )
        return data

    def normalize_data_rows_file(self, raws_file: list = []):
        rows = []
        for row in raws_file:
            temp = dict()
            map_config_dict = normalize_map_config(self.map_config)
            for _col in map_config_dict.keys():
                try:
                    value = row[map_config_dict[_col]]
                    if value:
                        value = str(value)
                    temp.update({map_config_dict[_col]: value})
                except Exception as ex:
                    continue
            temp.update({'_meta': row.get('_meta', {})})
            rows.append(temp)
        return rows

    def filter_raws_data_temp(self, filters: dict = {}):
        data_import_file = json.loads(self.lib_import.json_data_last_cache)
        #
        _type = filters.get('type', None)
        _key = filters.get('key', None)

        args = {
            'valid': 'total_success',
            'invalid': 'total_errors',
            'processed': 'total_complete',
        }

        raws_index = []
        logger.info(self.info_import_file['summary'])
        try:
            __type_get_total = args.get(_type)
            if _type in args.keys():
                raws_index = self.info_import_file['summary'][__type_get_total]['raws_index']
            if _type in ['errors']:
                raws_index_valid = self.info_import_file['summary']['total_success']['raws_index']
                raws_index_complete = self.info_import_file['summary']['total_complete']['raws_index']
                if len(raws_index_complete) > 0:
                    raws_index = list(set(raws_index_valid) - set(raws_index_complete))
        except Exception as ex:
            logger.error(ex)

        #
        if _type:
            if _type in ['created', 'updated']:
                data_import_file = [row for row in data_import_file if
                                    row.get('_meta', {}).get('type', None) == _type and
                                    row.get('_meta', {}).get('complete', False) is True]
            else:
                data_import_file = [row for row in data_import_file if row['_meta']['number'] in raws_index]

        data_import_file = self.filter_raws_data_by_key(data_import_file=data_import_file, key=_key)
        return data_import_file

    def filter_raws_data_by_key(self, data_import_file, key: str):
        if not key:
            return data_import_file

        def find_key(raw: dict = {}):
            for target_col in self.map_cols_obj.keys():
                _key = key
                _convert = None
                _value_raw = raw.get(self.map_cols_obj.get(target_col, None), None)
                try:
                    if re.search(key, str(_value_raw)):
                        return True
                except Exception as ex:
                    continue
            return False

        if key:
            # later
            return [_raw for _raw in data_import_file if find_key(_raw)]

    def download_file(self, file_path: str = None):
        file_path = os.path.join(file_path)
        file_handle = FileWrapper(open(file_path))
        mime_type, _ = mimetypes.guess_type(file_path)[0]
        response = FileResponse(file_handle, content_type=mime_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' % 'test.csv'
        return response
