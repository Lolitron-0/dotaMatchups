# Generated by Django 3.2.4 on 2021-06-16 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0009_auto_20210612_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='matchId',
            field=models.BigIntegerField(default=0, verbose_name='matchId'),
            preserve_default=False,
        ),
    ]
