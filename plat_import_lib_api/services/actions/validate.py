import copy
import itertools
import logging
import maya

from .base import LibBaseAction
from ..utils.exceptions import InvalidParamException
from ...static_variable.action import VALIDATE_ACTION
from ..utils.utils import round_up_currency
from ...static_variable.config import PLAT_IMPORT_DATETIME_DISPLAY_FORMAT

logger = logging.getLogger(__name__)


class LibValidateAction(LibBaseAction):
    JOB_ACTION = VALIDATE_ACTION

    def __init__(self, lib_import_id: str, map_config_request: list, **kwargs):
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        self.map_config_request = map_config_request
        self.validate_map_config_request()

    def validate_map_config_request(self):
        try:
            assert self.map_config_request is not None, f"Map config request not in config"
            target_cols_keys = [item['name'] for item in self.lib_module.target_cols]
            upload_col_keys = [item['name'] for item in self.info_import_file.get('cols_file')]
            for item in self.map_config_request:
                if not item['upload_col']:
                    continue
                assert item[
                           'target_col'] in target_cols_keys, f"'{item['target_col']}' target col request not in config"
                assert item['upload_col'] in upload_col_keys, f"'{item['upload_col']}' target col request not in config"
        except Exception as ex:
            raise InvalidParamException(message=ex, verbose=True)

    def merge_map_config_cols(self):
        map_config_request = {item['target_col']: item['upload_col'] for item in self.map_config_request}
        map_config = []
        for item in self.map_config:
            _item = copy.deepcopy(item)
            try:
                _upload_request = map_config_request[_item['target_col']]
                if _upload_request != _item['upload_col']:
                    _item['upload_col'] = _upload_request
            except Exception as ex:
                pass
            map_config.append(_item)
        if len(map_config) > 0:
            self.map_config = map_config
            self.info_import_file['map_cols_to_module'] = self.map_config

    def process(self):
        # merge map config request to map config exist
        self.merge_map_config_cols()
        #
        chunks_remain = copy.deepcopy(self.chunks_raws_file)

        self.reset_summary()
        self.update_to_lib_import()

        #
        for chunk in self.chunks_raws_file:
            del chunks_remain[0]
            logger.info("validate chunk size: {}".format(len(chunk)))

            self._process_raws(rows=chunk)

            total_remain_record = list(itertools.chain.from_iterable(copy.deepcopy(chunks_remain)))
            raws_file = self.chunks_list_process + total_remain_record

            # update done
            self.update_to_lib_import(raws_file)

    def reset_summary(self):
        self.info_import_file['summary']['total_errors']['count'] = 0
        self.info_import_file['summary']['total_errors']['raws_index'] = []

        #
        self.info_import_file['summary']['total_success']['count'] = 0
        self.info_import_file['summary']['total_success']['raws_index'] = []

    def add_count_process(self, total_type: str):
        self.info_import_file['summary'][total_type]['count'] += 1

    def add_raw_number_process(self, total_type: str, raw_index: any):
        self.info_import_file['summary'][total_type]['raws_index'].append(raw_index)

    def _process_raws(self, rows: list = []):
        for row in rows:
            self.validate_raw_temp_to_rule(row=row)
        self.chunks_list_process += rows

    def validate_raw_temp_to_rule(self, row: dict = None):
        data_request = {}

        # serializer
        target_cols = self.lib_module.target_cols
        map_config_dict = {item['target_col']: item['upload_col'] for item in self.map_config}

        for item in target_cols:
            _upload_col_name = map_config_dict.get(item['name'], None)
            if not _upload_col_name:
                continue
            _upload_col_val = row.get(_upload_col_name, None)
            if _upload_col_val and item['type'] in ['float', 'number']:
                try:
                    # round up with next cent
                    _upload_col_val = float(_upload_col_val)
                    _upload_col_val = round_up_currency(_upload_col_val)
                    row[_upload_col_name] = str(_upload_col_val)
                except Exception as ex:
                    logger.error(f"[{self.__class__.__name__}][round_up_currency] ex")
                    pass
            if _upload_col_val and item['type'] == 'datetime':
                try:
                    date_time_parsed = maya.parse(_upload_col_val)
                    _upload_col_val = date_time_parsed.datetime().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
                    row[_upload_col_name] = date_time_parsed.strftime(PLAT_IMPORT_DATETIME_DISPLAY_FORMAT)
                except Exception as ex:
                    pass
            data_request[item['name']] = _upload_col_val

        self.validate_data_request(data_request, row)

    def validate_data_request(self, data_request: dict, row: dict = {}, **kwargs):
        if not row:
            raise NotImplementedError
        data_validation, errors = super().validate_data_request(data_request=data_request)

        _errors = []
        for key in errors:
            msg = self.lib_module.handler_message_error_column_validate(self.lib_import_id, key,
                                                                        data_request.get(key), errors[key])
            item = {
                'code': key,
                'message': msg
            }
            _errors.append(item)
        if len(_errors) > 0:
            row['_meta']['valid'] = False
            row['_meta']['validation_errors'] = _errors
            self.add_count_process('total_errors')
            self.add_raw_number_process('total_errors', row['_meta']['number'])
        else:
            row['_meta']['valid'] = True
            row['_meta']['validation_errors'] = []
            self.add_count_process('total_success')
            self.add_raw_number_process('total_success', row['_meta']['number'])
        return data_validation
