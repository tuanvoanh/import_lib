import logging
from plat_import_lib_api.services.controllers.controller import ImportController
from celery.task import task

logger = logging.getLogger(__name__)


@task(name='lib_import_process_action_job')
def lib_import_process_action_task(lib_import_id: str, action: str, map_config_request: list = []):
    assert lib_import_id is not None, "Import temp id is not None"
    logger.info(f"[{lib_import_id}][{action}][lib_import_process_action_task] Begin lib_import_process_action_task")
    controller = ImportController(lib_import_id=lib_import_id, action=action, map_config_request=map_config_request)
    controller.process()
