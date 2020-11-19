import logging
import os
from plat_import_lib_api.static_variable.config import PLAT_IMPORT_STORAGE_FOLDER, MEDIA_ROOT
from ..models import DataImportTemporary, UPLOADING, VALIDATING, PROCESSING
from rest_framework import serializers
from django.conf import settings
from ..services.files.storage import StorageFileManage, STORAGE_UPLOAD_ACTION
from ..services.utils.response import ResponseDataService
from ..services.controllers.manage import ImportJobManager
from ..services.utils.utils import load_lib_module
from ..static_variable.action import UPLOAD_ACTION, VALIDATE_ACTION, PROCESS_ACTION
from ..sub_serializers.common_serializer import ColumnsMappingResponseSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from ..services.utils.utils import create_path_file
from django.utils import timezone

logger = logging.getLogger(__name__)


class LibImportModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataImportTemporary
        fields = '__all__'
        extra_fields = {
            'id': {'read_only': True},
            'created': {'read_only': True},
            'modified': {'read_only': True},
        }

    def to_representation(self, instance):
        instance.refresh_from_db()
        response = ResponseDataService(lib_import_id=str(instance.pk))
        return response.data_import

    def map_info_file(self, file_path: any, module: str, data: dict):
        try:
            storage_service = StorageFileManage(file_path=file_path, module=module, action=STORAGE_UPLOAD_ACTION)
            file_path = storage_service.process()
            logger.info(f"File path : {file_path}")
            data.update(temp_file_path=file_path)
        except Exception as ex:
            logger.error(f'[LibImportModelSerializer][storage_file]: {ex}')
            raise NotImplementedError

    @staticmethod
    def make_temp_file_inmemory(module, file):
        _, ext = os.path.splitext(file.name)
        file_path = create_path_file(file.name, module, "temp")
        default_storage.save(file_path, ContentFile(file.read()))
        return os.path.join(MEDIA_ROOT, file_path)

    def create(self, validation_data):

        # upload file and get info file
        request = self.context.get('request')
        # created record lib import
        kwargs = self.context['view'].kwargs
        module = kwargs.get('module')

        lib_module = load_lib_module(module)
        meta = lib_module.setup_metadata(self.context)
        data = dict(
            module=module,
            meta=meta,
            status=UPLOADING,
            progress=0
        )
        file = request.FILES.get('file')

        if isinstance(file, InMemoryUploadedFile):
            file_path = self.make_temp_file_inmemory(module, file)
        else:
            file_path = file.file.name
        self.map_info_file(file_path=file_path, data=data, module=module)
        return DataImportTemporary.objects.create(**data)

    def do_action_job(self, import_lib: DataImportTemporary, action: str, map_config_request: list = []):
        job_manage = ImportJobManager(lib_import_id=import_lib.pk, action=action, map_config_request=map_config_request)
        job_manage.process()


class UploadDataImportSerializer(LibImportModelSerializer):
    file = serializers.FileField(required=True)

    class Meta(LibImportModelSerializer.Meta):
        fields = ['file']

    def create(self, validation_data):
        import_lib = super().create(validation_data)
        self.do_action_job(import_lib=import_lib, action=UPLOAD_ACTION)
        return import_lib


class ValidateDataImportSerializer(LibImportModelSerializer):
    column_mapping = serializers.ListField(allow_empty=False, child=ColumnsMappingResponseSerializer(), write_only=True)

    class Meta(LibImportModelSerializer.Meta):
        fields = ('column_mapping',)

    def update(self, instance, validation_data):
        data = dict(
            status=VALIDATING,
            progress=0,
            validation_started=timezone.now(),
            validation_completed=None
        )
        DataImportTemporary.objects.filter(pk=instance.pk).update(**data)
        map_config_request = validation_data['column_mapping']
        self.do_action_job(import_lib=instance, action=VALIDATE_ACTION, map_config_request=map_config_request)
        return instance


class ProcessDataImportSerializer(LibImportModelSerializer):

    def update(self, instance, validation_data):
        data = dict(
            status=PROCESSING,
            progress=0,
            process_started=timezone.now(),
            process_completed=None
        )
        DataImportTemporary.objects.filter(pk=instance.pk).update(**data)
        self.do_action_job(import_lib=instance, action=PROCESS_ACTION)
        return instance


class ItemsDataImportSerializer(LibImportModelSerializer):
    def to_representation(self, instance):
        instance.refresh_from_db()
        request = self.context.get('request')
        key = request.query_params.get('key', None)
        if not key:
            key = request.query_params.get('s', None)
        filters = {
            'type': request.query_params.get('type', None),
            'key': key
        }
        limit = request.query_params.get('limit', 20)
        page = request.query_params.get('page', 1)
        response = ResponseDataService(lib_import_id=str(instance.pk))
        data = response.items_import(limit=limit, page=page, filters=filters)
        return data


class ExportSampleSerializer(serializers.Serializer):
    file_uri = serializers.CharField()


class ExportDataImportSerializer(LibImportModelSerializer):
    file_uri = serializers.CharField()

    class Meta(LibImportModelSerializer.Meta):
        fields = ('file_uri',)

    def to_representation(self, instance):
        try:
            instance.refresh_from_db()
            # get module
            lib_module = load_lib_module(instance.module)

            # temp data
            type_filter = self.context.get('type_filter')
            filters = {'type': type_filter}
            # data
            url = lib_module.export(lib_import_id=str(instance.pk), filters=filters)
            data = {'file_uri': url}
            return data
        except Exception as ex:
            logger.error(f'[ExportDataImportSerializer]: {ex}')
