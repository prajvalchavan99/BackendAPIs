# Generated by Django 4.2.6 on 2024-02-16 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tempupload', '0004_remove_uploadedfile_file_data_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='file',
            field=models.CharField(max_length=200, null=True),
        ),
    ]