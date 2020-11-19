from .controller import ImportController
from ...static_variable.config import PLAT_IMPORT_USE_QUEUE
from ...tasks import lib_import_process_action_task


class ImportJobManager(ImportController):

    def process(self):
        if PLAT_IMPORT_USE_QUEUE:
            lib_import_process_action_task.delay(lib_import_id=self.lib_import_id, action=self.action,
                                                 map_config_request=self.map_config_request)
        else:
            lib_import_process_action_task(lib_import_id=self.lib_import_id, action=self.action,
                                           map_config_request=self.map_config_request)
