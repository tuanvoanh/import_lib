# Generated by Django 2.2.2 on 2020-11-12 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plat_import_lib_api', '0011_auto_20201020_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='asintest',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]
