# Generated by Django 3.2.4 on 2021-06-28 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0013_auto_20210621_2349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='article',
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
