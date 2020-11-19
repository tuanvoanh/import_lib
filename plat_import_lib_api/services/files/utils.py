import os
import re
import random
import string
from datetime import timedelta
import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile

from django.utils.datetime_safe import datetime

from plat_import_lib_api.services.utils.utils import get_bucket_google_storage
from plat_import_lib_api.static_variable.config import PLAT_IMPORT_STORAGE, MEDIA_URL, BASE_URL, \
    GOOGLE_CLOUD_STORAGE_BUCKET_NAME, PLAT_IMPORT_STORAGE_FOLDER, MEDIA_ROOT


def suggest_upload_column_to_target_column(target_cols: list, upload_cols: list):
    assert len(target_cols) > 0, "Target column is not empty"
    assert len(upload_cols) > 0, "Upload column is not empty"
    config_mapping = []
    for target in target_cols:
        regex_detector = target['name_detector']
        if not regex_detector:
            label = target['label']
            regex_detector = [f"{label}"]
            regex_split = f"({label.replace(' ', '|')})"
            regex_detector.append(regex_split)
        __upload_find = search_col(regex_detector, upload_cols)
        __item = {
            'target_col': target['name'],
            'upload_col': __upload_find.get('name')
        }
        config_mapping.append(__item)
    return config_mapping


def search_col(regex_detector, upload_cols):
    for regex in regex_detector:
        __find = re.compile(regex, re.IGNORECASE)
        for upload in upload_cols:
            try:
                val = __find.search(upload['label'])
                if val:
                    return upload
            except Exception as ex:
                continue
    return {}


def generate_file_path_sample(module: str, version: str = '1.0'):
    file_path = None
    if PLAT_IMPORT_STORAGE == 'local':
        file_path = f"{PLAT_IMPORT_STORAGE_FOLDER}/{module}/templates/sample-v{version}.xlsx"
    if PLAT_IMPORT_STORAGE == 'google':
        file_path = f'{PLAT_IMPORT_STORAGE_FOLDER}/{module}/templates/sample-v{version}.xlsx'
    return file_path


def generate_url_sample(module: str, version: str = '1.0'):
    url = None
    file_path = generate_file_path_sample(module, version)
    if PLAT_IMPORT_STORAGE == 'local':
        file_storage = os.path.join(MEDIA_ROOT, file_path)
        url = f'{BASE_URL}{MEDIA_URL}{file_path}'
        if os.path.isfile(file_storage):
            return url, True
    if PLAT_IMPORT_STORAGE == 'google':
        url = f'https://storage.googleapis.com/{GOOGLE_CLOUD_STORAGE_BUCKET_NAME}/{file_path}'
        bucket = get_bucket_google_storage()
        blob = bucket.blob(file_path)
        if blob.exists():
            return url, True
    return url, False


def generate_string_and_digits(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_string(size=2, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_digits(size=2, digits=string.digits):
    return ''.join(random.choice(digits) for _ in range(size))


def generate_file_sample(module, target_cols: list, version: str = 1.0, number: int = 5):
    headers = [col['label'] for col in target_cols]
    data_rows = {}
    for target in target_cols:
        _label = target['label']
        _type = target['type']
        if _type in ['string']:
            _data = []
            for i in range(number):
                value = f'{generate_string(3)} {generate_string(3)}'
                _data.append(value)
            data_rows[_label] = _data
            continue
        if _type in ['integer']:
            _data = []
            for i in range(number):
                value = random.randint(0, 100)
                _data.append(value)
            data_rows[_label] = _data
            continue
        if _type in ['float', 'number']:
            _data = []
            for i in range(number):
                value = float("{0:.2f}".format(random.uniform(0000, 9999)))
                _data.append(value)
            data_rows[_label] = _data
            continue
        if _type in ['datetime']:
            _data = []
            for i in range(number):
                value = datetime.now() - timedelta(days=i)
                _data.append(value)
            data_rows[_label] = _data
            continue
    df = pd.DataFrame(data_rows, columns=headers)
    file_path = generate_file_path_sample(module, version)
    if PLAT_IMPORT_STORAGE == 'local':
        file_storage = os.path.join(MEDIA_ROOT, file_path)
        default_storage.save(file_storage, ContentFile(''))
        df.to_excel(file_storage, index=False, header=True, sheet_name='Sheet1')

    if PLAT_IMPORT_STORAGE == 'google':
        f = NamedTemporaryFile(suffix='.xlsx')
        df.to_excel(f, index=False, header=True, sheet_name='Sheet1')
        f.seek(0)
        bucket = get_bucket_google_storage()
        blob = bucket.blob(file_path)
        __GS_UPLOAD_CONTENT_TYPE__ = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        blob.upload_from_file(f, content_type=__GS_UPLOAD_CONTENT_TYPE__)
        blob.make_public()
