import importlib
import logging

from ...static_variable.config import IMPORT_MODULE_TEMPLATE
from ...services.utils.exceptions import InvalidModuleException
from django.conf import settings

logger = logging.getLogger(__name__)


class ModuleImportService(object):

    def __init__(self, name: str):
        assert name is not None, f"[{self.__class__.__name__}] Module name is not none"
        self.module = name

    def get_module_define(self):
        # Get setting from environment
        try:
            modules = importlib.import_module(IMPORT_MODULE_TEMPLATE)
            class_ = getattr(modules, self.module)
            instance = class_()
            return instance
        except Exception as ex:
            raise InvalidModuleException(
                message=f"[{self.__class__.__name__}] {self.module} not found settings config IMPORT_MODULE_TEMPLATE or error validate NotImplementedError in {self.module}",
                verbose=True)

    def load_module(self):
        return self.get_module_define()
