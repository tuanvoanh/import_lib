import os, csv, tempfile
from plat_import_lib_api.services.utils.exceptions import InvalidFormatException
from .storage import StorageFileManage, STORAGE_UPLOAD_ACTION
from ..objects.lib_import import LibImportObject
from ..utils.response import ResponseDataService
from ..utils.utils import normalize_map_config
from xlsxwriter.workbook import Workbook

CSV = 'csv'
EXCEL_XLSX = 'xlsx'
EXCEL_XLS = 'xls'


class ExportService(LibImportObject):

    def __init__(self, lib_import_id: str, file_type: str = 'xlsx', filters: dict = {}, **kwargs):
        self.file_type = file_type
        super().__init__(lib_import_id=lib_import_id, **kwargs)

        self.filters = filters

        self.type = self.filters.get('type', None)

        self.key = self.filters.get('key', None)

        self.response = ResponseDataService(lib_import_id=self.lib_import_id, **kwargs)

        self.map_cols_dict = normalize_map_config(self.map_config)

        self.file_name = None
        self.temp_file_path = None

        self.init_temp_file()

    def validate(self):
        assert self.file_type in [CSV, EXCEL_XLS, EXCEL_XLSX], "file type export is invalid"

    def init_temp_file(self):
        self.file_name = f'{self.lib_import.module}-{self.lib_import_id}-{self.type}.{self.file_type}'
        self.temp_file_path = os.path.join(tempfile.gettempdir(), self.file_name)

    def process(self):
        raws_data = self.response.filter_raws_data_temp(filters=self.filters)
        if self.file_type in ['csv']:
            return self.export_data_to_file_csv(raws_data=raws_data)
        if self.file_type in ['xlsx', 'xls']:
            return self.export_data_to_file_excel(raws_data=raws_data)
        raise InvalidFormatException(
            message='[ExportDataImportService][export_data_to_file] Invalid file type for export')

    @staticmethod
    def export_module_sample(name: str = None, target_cols: list = [], type: str = None):
        pass

    @property
    def category(self):
        category = self.type
        if not category:
            category = 'all'
        return f'export/{category}'

    def upload_file(self):
        storage_manager = StorageFileManage(file_path=self.temp_file_path, module=self.lib_import.module,
                                            action=STORAGE_UPLOAD_ACTION, public_url=True, category=self.category)
        file_path = storage_manager.process()
        return file_path

    def export_data_to_file_excel(self, raws_data: list = None):
        if not raws_data:
            return None
        # Create an new Excel file and add a worksheet.
        workbook = Workbook(self.temp_file_path)
        worksheet = workbook.add_worksheet()

        # Widen the first column to make the text clearer.
        worksheet.set_column('A:A', 20)

        # Add a cell format with text wrap on.
        cell_format = workbook.add_format({'text_wrap': True, 'color': 'red'})

        # get cols name
        _start_col_file = 0
        # add result column
        if self.type in ['invalid', 'error']:
            # add col result ro file export error
            worksheet.write(0, _start_col_file, 'Result', cell_format)
            _start_col_file = 1  # next col index

        # write head cols to file row 0
        for _index_col, _target_col in enumerate(self.lib_module.target_cols):
            worksheet.write(0, _start_col_file, _target_col['label'])
            _start_col_file += 1

        # reset index col
        _start_col_result_file = 0
        _start_col_next_file = 0

        # normalize name and label of target cols
        target_cols_label = {item['name']: item['label'] for item in self.lib_module.target_cols}

        for _index_row, _raw in enumerate(raws_data):
            if self.type in ['invalid', 'error']:
                errors = _raw['_meta']['validation_errors'] if self.type == 'invalid' else _raw['_meta'][
                    'processing_errors']
                errors_string_text = ''
                for error in errors:
                    code = error.get('code', None)
                    col_label = target_cols_label.get(code, None)
                    if not col_label:
                        errors_string_text += "\n\u2022 {message}\n".format(message=",".join(error['message']))
                    else:
                        errors_string_text += "\n\u2022 {column} column {message}\n".format(column=col_label,
                                                                                            message=",".join(
                                                                                                error['message']))
                worksheet.write(_index_row + 1, _start_col_result_file, errors_string_text, cell_format)
                _start_col_next_file = 1  # next col file
            for _index_col, _target_col in enumerate(self.map_cols_dict.keys()):
                worksheet.write(_index_row + 1, _index_col + _start_col_next_file,
                                _raw.get(self.map_cols_dict[_target_col], None))
        workbook.close()

        return self.upload_file()

    def export_data_to_file_csv(self, raws_data: list = None):
        if not raws_data:
            return None
        if not raws_data:
            return None
        # get cols name

        with open(self.temp_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            head_cols = []
            for _item in self.lib_module.target_cols:
                head_cols.append(_item['label'])
            writer.writerow(head_cols)
            # generate data
            for _raw in raws_data:
                data = []
                for _col in self.map_cols_dict.keys():
                    data.append(_raw[self.map_cols_dict[_col]])
                writer.writerow(data)
        return self.upload_file()
