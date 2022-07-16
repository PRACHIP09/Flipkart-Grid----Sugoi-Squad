# Generated by Django 4.0.6 on 2022-07-15 07:54

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='offer_price',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.upload_path_handler),
        ),
        migrations.AlterField(
            model_name='video',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=api.models.upload_path_handler),
        ),
    ]