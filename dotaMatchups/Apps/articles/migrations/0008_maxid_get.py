# Generated by Django 3.2.4 on 2021-06-12 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_rename_data_match_pair'),
    ]

    operations = [
        migrations.AddField(
            model_name='maxid',
            name='get',
            field=models.IntegerField(default=0, verbose_name='latestId'),
            preserve_default=False,
        ),
    ]
