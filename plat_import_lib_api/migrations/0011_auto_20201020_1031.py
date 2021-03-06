# Generated by Django 2.2.2 on 2020-10-20 10:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('plat_import_lib_api', '0010_auto_20201019_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataimporttemporary',
            name='client_id',
            field=models.UUIDField(null=True),
        ),
        migrations.AddIndex(
            model_name='dataimporttemporary',
            index=models.Index(fields=['module', 'client_id'], name='module_client_id_idx'),
        ),
    ]
