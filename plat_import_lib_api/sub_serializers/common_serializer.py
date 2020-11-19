from ..models import STATUS_CHOICE
from rest_framework import serializers
from drf_yasg import openapi


### SCHEMA FILE UPLOAD #####

class UploadDataImportSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class ColumnsMappingResponseSerializer(serializers.Serializer):
    target_col = serializers.CharField(required=True)
    upload_col = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        ref_name = 'column_mapping'


class SummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    valid = serializers.IntegerField()
    complete = serializers.IntegerField()

    class Meta:
        ref_name = 'summary'


class ColumnsSerializer(serializers.Serializer):
    name = serializers.CharField()
    label = serializers.CharField()

    class Meta:
        ref_name = 'column_schema'


class TargetColumnsSerializer(ColumnsSerializer):
    type = serializers.CharField()

    class Meta:
        ref_name = 'target_column_schema'


class DataImportResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    label = serializers.CharField()
    meta = serializers.DictField()
    progress = serializers.IntegerField(default=0)
    status = serializers.ChoiceField(choices=STATUS_CHOICE, default=STATUS_CHOICE[0][0])
    summary = SummarySerializer()
    columns = serializers.ListField(child=TargetColumnsSerializer())
    upload_columns = serializers.ListField(child=ColumnsSerializer())
    column_mapping = serializers.ListField(child=ColumnsMappingResponseSerializer())
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()

    class Meta:
        ref_name = 'response_schema'


### SCHEMA DATA RESPONSE #####

class MetaErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.ListField()

    class Meta:
        ref_name = 'meta_error_schema'


class MetaItemSerializer(serializers.Serializer):
    number = serializers.IntegerField()
    valid = serializers.BooleanField(default=False)
    complete = serializers.BooleanField(default=False)
    validation_errors = serializers.ListField(child=MetaErrorSerializer())
    processing_errors = serializers.ListField(child=MetaErrorSerializer())

    class Meta:
        ref_name = 'meta_item_schema'


class ItemSerializer(serializers.Serializer):
    column_name_1 = serializers.CharField()
    column_name_2 = serializers.CharField()
    column_name_n = serializers.CharField()
    __meta = MetaItemSerializer()

    class Meta:
        ref_name = 'item_schema'


class ItemsListSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    page_current = serializers.IntegerField()
    page_count = serializers.IntegerField()
    page_size = serializers.IntegerField()
    items = serializers.ListField(child=ItemSerializer())

    class Meta:
        ref_name = 'item_list_schema'
