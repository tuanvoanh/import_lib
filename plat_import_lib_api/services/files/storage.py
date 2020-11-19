import os

from plat_import_lib_api.services.utils.utils import get_extension_file, upload_file_to_gcloud, upload_file_to_local, \
    download_file_google
from plat_import_lib_api.static_variable.config import PLAT_IMPORT_STORAGE, MEDIA_ROOT, MEDIA_URL, BASE_URL

STORAGE_UPLOAD_ACTION = 'UPLOAD'
STORAGE_DOWNLOAD_ACTION = 'DOWNLOAD'


class StorageFileManage:

    def __init__(self, file_path: str, module: str, action: str, public_url: bool = False,
                 category: str = 'uploader', **kwargs):
        self.file_path = file_path
        self.module = module
        self.action = action
        self.public_url = public_url
        self.category = category

        self.file_name = None
        self.file_extension = None
        self.get_info_file_extension()

    def get_info_file_extension(self):
        self.file_name, self.file_extension = get_extension_file(self.file_path)

    def validate(self):
        assert self.action in [STORAGE_UPLOAD_ACTION,
                               STORAGE_DOWNLOAD_ACTION], f"type {self.action} action not in [STORAGE_UPLOAD_ACTION, STORAGE_DOWNLOAD_ACTION]"
        assert self.module is not None, f"Module storage service is not None"

    def process(self):
        path_file = None
        if self.action == STORAGE_UPLOAD_ACTION:
            if PLAT_IMPORT_STORAGE == 'local':
                path_file = upload_file_to_local(file_path=self.file_path, module=self.module, category=self.category)
                if self.public_url:
                    path_file = f'{BASE_URL}{MEDIA_URL}{path_file}'
                else:
                    path_file = os.path.join(MEDIA_ROOT, path_file)
            if PLAT_IMPORT_STORAGE == 'google':
                path_file = upload_file_to_gcloud(file_path=self.file_path, module=self.module, category=self.category)
        if self.action == STORAGE_DOWNLOAD_ACTION:
            if PLAT_IMPORT_STORAGE == 'google':
                path_file = download_file_google(file_path=self.file_path, module=self.module, category=self.category)
        return path_file
