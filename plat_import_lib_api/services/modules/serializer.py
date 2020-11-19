from django.db.models import TextField
from rest_framework.fields import CharField, FloatField, IntegerField, DecimalField, DateTimeField, ChoiceField, \
    UUIDField


class SerializerHandle(object):

    def __init__(self, serializer: any, regex_pattern_map_config: dict, **kwargs):
        self.regex_pattern_map_config = regex_pattern_map_config
        self.serializer = serializer()
        self.kwargs = kwargs

    def get_regex_name_detector_column(self, field_name):
        try:
            return self.regex_pattern_map_config.get(field_name)
        except Exception as ex:
            return None

    @staticmethod
    def normalize_label(field_name, content_type):
        label = content_type.label
        if not label:
            label = field_name.replace('_', ' ').title()
        return label

    def get_column_config(self, name_detector: bool = False):
        rs = []
        columns = self.serializer.get_fields()
        for field in columns:
            content_type = columns[field]
            field_type = self.get_field_type(content_type)
            label = self.normalize_label(field, content_type)
            item = {
                'name': field,
                'label': label,
                'type': field_type
            }
            if name_detector:
                item.update({'name_detector': self.get_regex_name_detector_column(field)})
            rs.append(item)

        return rs

    @property
    def target_cols(self):
        return self.get_column_config(name_detector=True)

    @property
    def columns(self):
        return self.get_column_config()

    @staticmethod
    def get_field_type(content_type):
        if isinstance(content_type, CharField) or isinstance(content_type, TextField) or isinstance(content_type,
                                                                                                    ChoiceField) \
                or isinstance(content_type, UUIDField):
            return "string"
        if isinstance(content_type, DecimalField):
            return "number"
        if isinstance(content_type, FloatField):
            return "float"
        if isinstance(content_type, IntegerField):
            return "integer"
        if isinstance(content_type, DateTimeField):
            return "datetime"
        return None
