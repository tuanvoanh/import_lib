# Generated by Django 2.2.2 on 2020-07-02 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plat_import_lib_api', '0005_auto_20200626_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asintest',
            name='asin',
            field=models.CharField(max_length=100, verbose_name='Asin'),
        ),
        migrations.AlterField(
            model_name='asintest',
            name='brand',
            field=models.CharField(max_length=100, verbose_name='Brand'),
        ),
        migrations.AlterField(
            model_name='asintest',
            name='cost',
            field=models.FloatField(verbose_name='Cost'),
        ),
        migrations.AlterField(
            model_name='asintest',
            name='domain',
            field=models.CharField(max_length=100, verbose_name='Domain'),
        ),
        migrations.AlterField(
            model_name='asintest',
            name='frequency',
            field=models.CharField(max_length=100, verbose_name='Frequency'),
        ),
        migrations.AlterField(
            model_name='asintest',
            name='profile_id',
            field=models.CharField(max_length=100, verbose_name='Profile Id'),
        ),
        migrations.AlterField(
            model_name='asintest',
            name='sku',
            field=models.CharField(max_length=100, verbose_name='Sku'),
        ),
        migrations.AlterField(
            model_name='asintest',
            name='upc',
            field=models.FloatField(verbose_name='Upc'),
        ),
    ]
