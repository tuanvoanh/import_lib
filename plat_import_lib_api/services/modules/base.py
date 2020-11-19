import copy
import logging
import uuid
from django.db import models
from rest_framework.permissions import AllowAny
from .serializer import SerializerHandle
from ..files.utils import generate_file_sample, generate_url_sample
from ...models import AsinTest as AsinTestModel
from ...services.files.export import ExportService
from ...services.actions.upload import LibUploadAction
from ...services.actions.validate import LibValidateAction
from ...services.actions.process import LibProcessAction
from ...sub_serializers.asin_test_serializer import AsinTestSerializer

logger = logging.getLogger('django')


class BaseModule(object):
    __NAME__ = None
    __MODEL__ = models.Model
    __LABEL__ = None
    __TEMPLATE_VERSION__ = '1.0'
    __SERIALIZER_CLASS__ = None
    __PERMISSION_CLASS__ = []  # permissions class setup to api view

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.serializer_handle = SerializerHandle(serializer=self.serializer_class,
                                                  regex_pattern_map_config=self.regex_pattern_map_config,
                                                  **self.kwargs)

        self.validate_module()

    @property
    def permissions_class(self):
        return self.__PERMISSION_CLASS__

    def validate_module(self):
        if not self.__SERIALIZER_CLASS__:
            raise NotImplementedError
        if not self.__PERMISSION_CLASS__:
            raise NotImplementedError

    @property
    def name(self):
        return self.__NAME__

    @property
    def label(self):
        return self.__LABEL__

    @property
    def model(self):
        return self.__MODEL__

    @property
    def template(self):
        url, exist = generate_url_sample(self.__NAME__, self.__TEMPLATE_VERSION__)
        if exist:
            return url
        generate_file_sample(self.__NAME__, self.serializer_handle.target_cols, self.__TEMPLATE_VERSION__)
        return url

    @property
    def serializer_class(self):
        return self.__SERIALIZER_CLASS__

    @property
    def columns(self) -> list:
        """
        public to api detail
        Structure:
            {
                name : <name column define serializer>,
                label : <label column define serializer>,
                type : <type column define serializer>
            }
        :return:
        """
        return self.serializer_handle.columns

    @property
    def target_cols(self) -> list:
        """
        using for handler background
        Structure:
            {
                name : <name column define serializer>,
                label : <label column define serializer>,
                type : <type column define serializer>,
                name_detector : <list regex pattern find map to upload column>
            }
        :return:
        """
        return self.serializer_handle.target_cols

    @property
    def regex_pattern_map_config(self):
        """
        document : https://docs.python.org/3.6/howto/regex.html
        Regex pattern for map target column to upload column with list regex pattern config
        structure:
            {
                '<name_column_define>: [...]
            }
        :return:
        """
        return {}

    def setup_metadata(self, context_serializer, **kwargs):
        """
        Method call when make record upload
        :param context_serializer:
        :return:
        """
        meta = {}
        request = context_serializer.get('request')
        params_request = context_serializer.get('view').kwargs
        try:
            for key in params_request.keys():
                val = params_request[key]
                if isinstance(val, uuid.UUID):
                    val = str(val)
                meta.update({key: val})
            meta.update({'user_id': request.user.user_id})
            meta.update(kwargs)
        except Exception as ex:
            logger.error(f'[BaseModule][setup_metadata][request] {ex}')
        return meta

    def handler_message_error_column_validate(self, lib_import_id: str, column: str, value: any, errors: list,
                                              **kwargs):
        return errors

    def handler_response_detail(self, response_data, **kwargs) -> dict:
        return response_data

    def validate_request_api_view(self, request, *args, **kwargs):
        raise NotImplementedError

    def upload(self, lib_import_id: str = None, **kwargs) -> any:
        service = LibUploadAction(lib_import_id=lib_import_id, **kwargs)
        service.process()

    def validate(self, lib_import_id: str, map_config_request: list, **kwargs) -> any:
        action = LibValidateAction(lib_import_id=lib_import_id, map_config_request=map_config_request, **kwargs)
        action.process()

    def process(self, lib_import_id: str, **kwargs) -> any:
        action = LibProcessAction(lib_import_id=lib_import_id, **kwargs)
        action.process()

    def export(self, lib_import_id: str, filters: dict = {}, **kwargs):
        export = ExportService(lib_import_id=lib_import_id, filters=filters)
        return export.process()

    def handler_validated_data(self, lib_import_id: str, validated_data: dict, **kwargs):
        """
        Handler validated data step process for make instance
        """
        return validated_data

    def filter_instance(self, lib_import_id: str, validated_data, **kwargs):
        """
        define filter instance for update case step process
        Structure :
            {
                column : validation_date[<name>]
            }
        """
        raise NotImplementedError

    @property
    def model_objects(self):
        if hasattr(self.model, 'all_objects'):
            model_objects = self.model.all_objects
        else:
            model_objects = self.model.objects
        return model_objects

    def find_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
        try:
            filters = self.filter_instance(lib_import_id, validated_data, **kwargs)
            return self.model_objects.get(**filters)
        except Exception as ex:
            logger.error(ex)
            return None

    def make_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
        instance = self.find_instance(lib_import_id, validated_data, **kwargs)
        created = True

        if instance:
            obj = copy.deepcopy(instance)
            for key, item in validated_data.items():
                setattr(obj, key, item)
            if hasattr(self.model, 'is_removed') and hasattr(self.model, 'all_objects'):
                setattr(obj, 'is_removed', False)
            created = False
        else:
            obj = self.model(**validated_data)
        return obj, created

    def handler_bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
        pass

    @property
    def field_model_accept_update(self):
        return [i.name for i in self.model._meta.fields if i.name not in ['pk', 'id']]

    def bulk_process(self, lib_import_id: str, bulk_insert: list, bulk_update: list, **kwargs):
        """
        process insert or update data per chunk list data step process
        """
        # handler pre bulk process
        self.handler_bulk_process(lib_import_id, bulk_insert, bulk_update, **kwargs)

        self.model_objects.bulk_create(bulk_insert, ignore_conflicts=True)
        self.model_objects.bulk_update(bulk_update, fields=self.field_model_accept_update)


class AsinTest(BaseModule):
    __NAME__ = "AsinTest"
    __MODEL__ = AsinTestModel
    __LABEL__ = "Asin Test"
    __SERIALIZER_CLASS__ = AsinTestSerializer
    __PERMISSION_CLASS__ = [AllowAny]

    @property
    def regex_pattern_map_config(self):
        return {
            'profile_id': ['profile id', f'(profile|pro id)'],
            'brand': [f'(brand|brand name)', 'brand'],
        }

    def filter_instance(self, lib_import_id: str, validated_data: dict, **kwargs):
        return {
            'brand': validated_data.get('brand'),
            'sku': validated_data.get('sku')
        }

    def validate_request_api_view(self, request, *args, **kwargs):
        pass

    def handler_cell_value_file_uploader(self, col_header: str, cell_val: any, map_config: list):
        pass
