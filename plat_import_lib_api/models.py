import uuid
from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel
from django.contrib.postgres.fields import JSONField

UPLOADING = 'uploading'
UPLOADED = 'uploaded'
VALIDATING = 'validating'
VALIDATED = 'validated'
PROCESSING = 'processing'
PROCESSED = 'processed'

STATUS_CHOICE = (
    (UPLOADING, 'Uploading'),
    (UPLOADED, 'Uploaded'),
    (VALIDATING, 'Validating'),
    (VALIDATED, 'Validated'),
    (PROCESSING, 'Processing'),
    (PROCESSED, 'Processed')
)

GOOGLE_TYPE = 'google'
LOCAL_TYPE = 'local'

TEMP_FILE_TYPE = (
    (GOOGLE_TYPE, 'Google Storage'),
    (LOCAL_TYPE, 'Local storage')
)


class DataImportTemporary(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.UUIDField(null=True)
    module = models.CharField(max_length=100)
    meta = JSONField(default=dict, verbose_name='meta data integrate import lib')
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default=STATUS_CHOICE[0][0],
                              verbose_name='status of file temp')
    log = models.TextField(verbose_name='log import data file', null=True, default=None)
    progress = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # progress percent of status
    total_process = models.IntegerField(verbose_name='Total process record by status', default=0)
    info_import_file = JSONField(default=dict, verbose_name='Info import file')
    temp_file_path = models.TextField(default=None, null=True)
    temp_file_path_type = models.CharField(max_length=20, choices=TEMP_FILE_TYPE, default=LOCAL_TYPE,
                                           verbose_name='Temp file path type')
    time_exc = models.TextField(default=None, null=True)
    json_data = models.TextField(default='{}', null=True, verbose_name='Json Data Origin')
    json_data_last_cache = models.TextField(default='{}', null=True, verbose_name="Json Data Last Cache")
    validation_started = models.DateTimeField(default=None, null=True)
    validation_completed = models.DateTimeField(default=None, null=True)
    process_started = models.DateTimeField(default=None, null=True)
    process_completed = models.DateTimeField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['module', 'client_id'], name='module_client_id_idx'),
        ]


class AsinTest(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_id = models.CharField(max_length=100, verbose_name="Profile Id")
    brand = models.CharField(max_length=100, verbose_name="Brand")
    upc = models.FloatField(verbose_name="Upc")
    asin = models.CharField(max_length=100, verbose_name="Asin")
    sku = models.CharField(max_length=100, verbose_name="Sku")
    domain = models.CharField(max_length=100, verbose_name="Domain")
    frequency = models.CharField(max_length=100, verbose_name="Frequency")
    cost = models.FloatField(verbose_name="Cost")
    posted_date = models.DateTimeField(blank=True, null=True, verbose_name="Posted Date")

    class Meta:
        unique_together = ('profile_id', 'brand', 'asin')
