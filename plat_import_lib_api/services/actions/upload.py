from .base import LibBaseAction
from ..files.read import ReaderFileManage
from ...static_variable.action import UPLOAD_ACTION


class LibUploadAction(LibBaseAction):
    JOB_ACTION = UPLOAD_ACTION

    def process(self):
        #
        service = ReaderFileManage(lib_import_id=self.lib_import_id)
        service.processing()
