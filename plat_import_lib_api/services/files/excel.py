import decimal, math, maya, logging, openpyxl, time
from django.conf import settings
from plat_import_lib_api.services.files.base import FileImportInterface
from ..utils.exceptions import InvalidFormatException
from ...static_variable.config import PLAT_IMPORT_DATETIME_DISPLAY_FORMAT, PLAT_IMPORT_DATA_CHUNK_SIZE

logger = logging.getLogger('django')


class ExcelImportObject(FileImportInterface):
    def validate(self):
        super().validate()
        if not self.file_path.endswith('.xlsx') and not self.file_path.endswith('.xls'):
            raise InvalidFormatException(message="File not valid type EXCEL")
        pass

    def load_workbook(self):
        self.wb = openpyxl.load_workbook(self.file_path)

    def get_header(self):
        worksheet = self.wb.worksheets[0]
        # init info
        cols_file = []
        columns_file = worksheet[1]  # get header
        for item in columns_file:
            cols_file.append(
                {
                    'label': str(item.value),
                    'name': str(item.value).replace(' ', '_').lower(),
                }
            )
        self.header = cols_file

    def get_total(self):
        self.total = self.wb.worksheets[0].max_row - 1  # exclude column header

    def process_row(self, row):
        _row_temp = {}
        for cell in row:
            if isinstance(cell.value, float) and math.isnan(cell.value):
                cell.value = None
        empty = not any((cell.value for cell in row))
        if empty:
            return _row_temp
        i = 0
        for cell in row:
            name_header = self.header[i]['name']
            if cell.is_date:
                try:
                    _temp_cell = maya.parse(cell.value).datetime().strftime(PLAT_IMPORT_DATETIME_DISPLAY_FORMAT)
                except Exception as ex:
                    _temp_cell = None
                _row_temp[name_header] = _temp_cell
                i += 1
                continue
            _temp_cell = cell.value
            if isinstance(_temp_cell, float) and math.isnan(_temp_cell):
                _temp_cell = None
                _row_temp[self.header[i]['name']] = _temp_cell
                i += 1
                continue
            _row_temp[name_header] = _temp_cell
            i += 1
        _row_temp['_meta'] = self.init_meta()
        return _row_temp

    def divide_chunks(self, l):
        n = PLAT_IMPORT_DATA_CHUNK_SIZE
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def chunk_size(self, l):
        start_number = 2  # start read row
        list_chunk = list(self.divide_chunks(range(l)))
        for index, value in enumerate(list_chunk):
            list_chunk[index] = list(map(lambda x: x + start_number, value))
        return list_chunk

    def process(self):
        try:
            self.init_info_import_file()
            worksheet = self.wb.worksheets[0]
            # update info
            raws_file = []
            #
            # start upload
            segments = self.chunk_size(self.total)
            #
            self.start_time = time.time()
            #
            for segment in segments:
                logger.info(f"processing read segment length : {len(segment)}")
                for row in worksheet.iter_rows(min_row=segment[0], max_row=segment[-1]):
                    _row_temp = self.process_row(row)
                    if not _row_temp:
                        self.num_row_empty += 1
                        continue
                    raws_file.append(_row_temp)
                    self.num_row += 1
                # cal percent chunk uploader
                self.total_progress += len(segment)
                self.update_process_upload(raws_file)
                #
                logger.info("complete processing segment length : {}".format(len(segment)))
            self.handle_final_upload()
            return self.info_import_file
        except Exception as ex:
            logger.error('[{}] ReadFile.read_data_file_excel: {}'.format(self.__class__.__name__, ex))
            raise ex
