from rest_framework import serializers

from plat_import_lib_api.models import AsinTest
from rest_framework.exceptions import ValidationError


class AsinTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = AsinTest
        fields = ['profile_id', 'brand', 'upc', 'asin', 'sku', 'domain', 'frequency', 'cost', 'posted_date']
        extra_kwargs = {
            'brand': {'required': True},
            'sku': {'required': True}
        }

    def validate_cost(self, value):
        errors = []
        if value < 0:
            errors.append("value is not negative")
        if errors:
            raise ValidationError(errors)
        return value
