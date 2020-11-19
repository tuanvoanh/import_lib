import time
from django.utils import timezone

from ..objects.lib_import import LibImportObject
from ...models import DataImportTemporary

from ...static_variable.action import UPLOAD_ACTION, VALIDATE_ACTION, PROCESS_ACTION, IMPORT_ACTION_LIST


class ImportController(LibImportObject):

    def __init__(self, lib_import_id: str, action: str, map_config_request: list, **kwargs):
        self.action = action
        super().__init__(lib_import_id=lib_import_id, **kwargs)
        self.map_config_request = map_config_request
        self.time_exec_start = time.clock()
        self.time_exec_end = self.time_exec_start

        self.data_update_complete = {}

    def validate(self):
        assert self.action in IMPORT_ACTION_LIST, "Action Controller is invalid"

    def process(self):
        if self.action == UPLOAD_ACTION:
            self.lib_module.upload(lib_import_id=self.lib_import_id, **self.kwargs)

        if self.action == VALIDATE_ACTION:
            self.lib_module.validate(lib_import_id=self.lib_import_id, map_config_request=self.map_config_request,
                                     **self.kwargs)
            self.data_update_complete.update({'validation_completed': timezone.now()})

        if self.action == PROCESS_ACTION:
            self.lib_module.process(lib_import_id=self.lib_import_id, **self.kwargs)
            self.data_update_complete.update({'process_completed': timezone.now()})

            self.time_exec_end = time.clock()
            self.update_process()

    def update_process(self):
        time_exc = self.time_exec_end - self.time_exec_start
        if time_exc > 0:
            self.data_update_complete.update({'time_exc': str(time_exc)})
        if self.data_update_complete:
            DataImportTemporary.objects.filter(pk=self.lib_import_id).update(**self.data_update_complete)
