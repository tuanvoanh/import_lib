from django.conf import settings

# environ config django
ENVIRONMENT = settings.ENVIRONMENT
BASE_URL = settings.BASE_URL
MEDIA_URL = settings.MEDIA_URL
MEDIA_ROOT = settings.MEDIA_ROOT

# info config of plat import in django environ
PLAT_IMPORT_USE_QUEUE = settings.PLAT_IMPORT_USE_QUEUE if hasattr(settings, 'PLAT_IMPORT_USE_QUEUE') else False

PLAT_IMPORT_DATA_CHUNK_SIZE = settings.PLAT_IMPORT_DATA_CHUNK_SIZE \
    if hasattr(settings, 'PLAT_IMPORT_DATA_CHUNK_SIZE') else 2000

PLAT_IMPORT_STORAGE = settings.PLAT_IMPORT_STORAGE \
    if hasattr(settings, 'PLAT_IMPORT_STORAGE') else 'local'

PLAT_IMPORT_ROUND_UP = settings.PLAT_IMPORT_ROUND_UP \
    if hasattr(settings, 'PLAT_IMPORT_ROUND_UP') else 0.0

PLAT_IMPORT_STORAGE_FOLDER = settings.PLAT_IMPORT_STORAGE_FOLDER \
    if hasattr(settings, 'PLAT_IMPORT_STORAGE_FOLDER') else 'pf/lib_imports'

# info google storage bucket
GOOGLE_CLOUD_STORAGE_BUCKET_NAME = settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME \
    if hasattr(settings, 'GOOGLE_CLOUD_STORAGE_BUCKET_NAME') else None
GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY = settings.GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY \
    if hasattr(settings, 'GOOGLE_CLOUD_STORAGE_BUCKET_ACCESS_KEY') else None

PLAT_IMPORT_DATETIME_DISPLAY_FORMAT = settings.PLAT_IMPORT_DATETIME_DISPLAY_FORMAT \
    if hasattr(settings, 'PLAT_IMPORT_DATETIME_DISPLAY_FORMAT') else '%Y-%m-%d %H:%M:%S'

IMPORT_MODULE_TEMPLATE = settings.IMPORT_MODULE_TEMPLATE \
    if hasattr(settings, 'IMPORT_MODULE_TEMPLATE') else 'plat_import_lib_api.modules.base'
