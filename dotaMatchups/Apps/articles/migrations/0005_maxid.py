# Generated by Django 3.2.4 on 2021-06-12 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_match'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaxId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LatestId', models.BigIntegerField(verbose_name='LatestId')),
            ],
        ),
    ]