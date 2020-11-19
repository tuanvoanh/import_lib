import pandas as pd, logging, time, math, maya
from django.conf import settings
from plat_import_lib_api.services.files.base import FileImportInterface
from ..utils.exceptions import InvalidFormatException
from ...static_variable.config import PLAT_IMPORT_DATA_CHUNK_SIZE

logger = logging.getLogger('django')


class CSVImportObject(FileImportInterface):

    def validate(self) -> None:
        super(CSVImportObject, self).validate()
        if not self.file_path.endswith('.csv'):
            raise InvalidFormatException(message="File not valid type EXCEL")
        pass

    def load_workbook(self):
        self.wb = pd.read_csv(self.file_path)

    def get_header(self):
        # init info
        cols_file = []
        columns = list(self.wb.columns)  # get header
        for value in columns:
            cols_file.append(
                {
                    'label': str(value),
                    'name': str(value).replace(' ', '_').lower(),
                }
            )
        self.header = cols_file

    def get_total(self):
        self.total = len(self.wb.index)

    def fetch_upload_cols_with_target_cols(self):
        map_cols_to_module = self.info_import_file.get('map_cols_to_module')
        self.map_upload_to_target_cols = {item['upload_col']: item['target_col'] for item in map_cols_to_module}

    def replace_last_dot_zero(self, _temp_cell):
        if ' ' not in _temp_cell and _temp_cell[-2:] == '.0':
            _temp_cell = _temp_cell.replace('.0', '')
        return _temp_cell

    def process_row(self, row, columns_file):
        _row_temp = {}
        for column in columns_file:
            if isinstance(row[column], float) and math.isnan(row[column]):
                row[column] = None
        empty = not any(row[column] for column in columns_file)
        if empty:
            return _row_temp
        # start index
        i = 0
        for column in columns_file:
            _col_header = self.header[i]['name']
            value = row[column]
            if value is not None:
                value = self.replace_last_dot_zero(value)
            _row_temp[_col_header] = value
            i += 1
        _row_temp['_meta'] = self.init_meta()
        return _row_temp

    def process(self):
        try:
            self.init_info_import_file()

            #
            self.fetch_upload_cols_with_target_cols()

            columns_file = list(self.wb.columns)
            # update info
            raws_file = []
            # start upload
            self.start_time = time.time()
            for segment in pd.read_csv(self.file_path, chunksize=PLAT_IMPORT_DATA_CHUNK_SIZE, dtype=str):
                logger.info(f"processing read segment length : {len(segment)}")
                for index, row in segment.iterrows():
                    _row_temp = self.process_row(row, columns_file)
                    if not _row_temp:
                        self.num_row_empty += 1
                        continue
                    raws_file.append(_row_temp)
                    self.num_row += 1
                # cal percent chunk uploader
                self.total_progress += len(segment)
                self.update_process_upload(raws_file)
                logger.info("complete processing segment length : {}".format(len(segment)))
            self.handle_final_upload()
        except Exception as ex:
            logger.error('ReadFile.read_data_file_csv: {}'.format(ex))
            raise InvalidFormatException(message=ex, verbose=True)
