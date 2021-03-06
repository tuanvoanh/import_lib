# Generated by Django 2.2.2 on 2020-03-17 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plat_import_lib_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataimporttemporary',
            name='completed',
        ),
        migrations.AddField(
            model_name='dataimporttemporary',
            name='progress',
            field=models.IntegerField(default=0, verbose_name='progress percent of status file temp'),
        ),
        migrations.AlterField(
            model_name='dataimporttemporary',
            name='status',
            field=models.CharField(choices=[('uploading', 'Uploading'), ('uploaded', 'Uploaded'), ('validating', 'Validating'), ('validated', 'Validated'), ('processing', 'Processing'), ('processed', 'Processed')], default='uploading', max_length=20, verbose_name='status of file temp'),
        ),
    ]
