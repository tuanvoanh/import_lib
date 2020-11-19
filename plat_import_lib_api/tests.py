import json
import os
import pathlib

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from plat_import_lib_api.models import AsinTest


@override_settings(
    BROKER_BACKEND="memory",
    PLAT_IMPORT_USE_QUEUE=False,
    PLAT_IMPORT_STORAGE="local"
)
class LibImportAPITest(APITestCase):

    def setUp(self):
        super().setUp()
        # file name
        self.file_name = 'asin_test.xlsx'
        self.module = 'AsinTest'

        self.total_records = 9

    def test_file_sample(self):
        # validate export all
        url = reverse('export-sample-data-import-of-module', kwargs={'module': self.module})
        rs = self.client.get(path=url, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['file_uri'] is not None, True)

    def _upload_import(self):
        url = reverse('upload-data-import-to-module', kwargs={'module': self.module})
        path_folder = pathlib.Path(__file__).parent.absolute()
        path_file = os.path.join(path_folder, 'fixtures', self.file_name)
        print(path_file)
        file = open(path_file, 'rb')
        data = {
            'file': file
        }
        rs = self.client.post(path=url, data=data, format='multipart')
        file.close()
        return rs

    def _verify_upload_file(self, rs):
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertIsNotNone(content, msg='Content is not None')
        print("process : {}".format(content.get('progress')))
        self.assertEqual(content["progress"], 100)
        self.assertEqual(content["status"], "uploaded")
        self.assertEqual(content["name"], self.module)
        self.assertEqual(content['summary']['total'], self.total_records)

    def test_upload_api(self):
        # file excel
        rs = self._upload_import()
        self._verify_upload_file(rs)

        # file csv
        self.file_name = 'asin_test.csv'
        rs = self._upload_import()
        self._verify_upload_file(rs)

    def _items_import(self, import_id):
        url = reverse('items-data-import-of-module', kwargs={'module': self.module, 'import_id': import_id})
        rs = self.client.get(path=url, format='json')
        return rs

    def _verify_items_import(self, rs):
        content = json.loads(rs.content.decode('utf-8'))

        print(content)
        import_id = content["id"]
        rs = self._items_import(import_id)
        print(rs)

        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content["total"], self.total_records)
        self.assertEqual(len(content["items"]), self.total_records)

    def test_get_items_sale_items_module(self):
        rs = self._upload_import()
        self._verify_items_import(rs)

        self.file_name = 'asin_test.csv'
        rs = self._upload_import()
        self._verify_items_import(rs)

    def validate_import(self, import_id, data):
        url = reverse('validate-data-import-of-module', kwargs={'module': self.module, 'import_id': import_id})
        rs = self.client.put(path=url, data=data, format='json')
        return rs

    def _validate_import(self):
        print("validate file name : {}".format(self.file_name))
        rs = self._upload_import()
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        import_id = content["id"]
        map_config = content['column_mapping']
        data = {
            "column_mapping": map_config
        }
        rs = self.validate_import(import_id, data)
        items = self._items_import(import_id)
        print(rs)
        print(items)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content["progress"], 100)
        self.assertEqual(content["summary"]["total"], self.total_records)
        self.assertEqual(content["summary"]["valid"], 7)
        self.assertEqual(content["status"], "validated")
        #
        return items

    def test_validate_module_import(self):
        rs_items_import = self._validate_import()

        print(rs_items_import)
        self.assertEqual(rs_items_import.status_code, status.HTTP_200_OK)
        content = json.loads(rs_items_import.content.decode('utf-8'))
        print(content)

        self.file_name = 'asin_test.csv'
        rs_items_import = self._validate_import()

        print(rs_items_import)
        self.assertEqual(rs_items_import.status_code, status.HTTP_200_OK)
        content = json.loads(rs_items_import.content.decode('utf-8'))
        print(content)

    def _process_import(self, import_id):
        url = reverse('process-data-import-of-module', kwargs={'module': self.module, 'import_id': import_id})
        rs = self.client.put(path=url, format='json')
        return rs

    def get_items_import(self, import_id):
        #
        rs = self._items_import(import_id)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        return content['items']

    def _validate_process_import(self):
        rs = self._upload_import()
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        import_id = content["id"]
        map_config = content['column_mapping']
        data = {
            "column_mapping": map_config
        }
        self.validate_import(import_id, data)
        # process import
        rs = self._process_import(import_id)
        print(rs)
        self.assertEqual(rs.status_code, status.HTTP_200_OK)
        content = json.loads(rs.content.decode('utf-8'))
        self.assertEqual(content['progress'], 100)
        self.assertEqual(content['summary']['total'], self.total_records)
        self.assertEqual(content['summary']['completed'], 7)
        self.assertEqual(content['status'], 'processed')

        #
        query_set = AsinTest.objects.all()
        self.assertEqual(query_set.count(), 7)

        # validate export all
        url = reverse('export-all-data-import-of-module', kwargs={'module': self.module, 'import_id': import_id})
        rs = self.client.get(path=url, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['file_uri'] is not None, True)

        # validate export invalid
        url = reverse('export-invalid-data-import-of-module', kwargs={'module': self.module, 'import_id': import_id})
        rs = self.client.get(path=url, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['file_uri'] is not None, True)

        # validate export error
        url = reverse('export-error-data-import-of-module', kwargs={'module': self.module, 'import_id': import_id})
        rs = self.client.get(path=url, format='json')
        content = json.loads(rs.content.decode('utf-8'))
        print(content)
        self.assertEqual(content['file_uri'] is None, True)

    def test_process_import(self):
        AsinTest.objects.all().delete()
        # file excel
        self._validate_process_import()

        AsinTest.objects.all().delete()
        self.file_name = 'asin_test.csv'
        self._validate_process_import()
