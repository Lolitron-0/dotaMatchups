# Generated by Django 3.2.4 on 2021-06-08 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20210608_1316'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]