# Generated by Django 2.2.2 on 2020-11-18 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plat_import_lib_api', '0012_asintest_is_removed'),
    ]

    operations = [
        migrations.AddField(
            model_name='asintest',
            name='posted_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Posted Date'),
        ),
    ]
