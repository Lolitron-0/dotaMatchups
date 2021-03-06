# Generated by Django 3.2.4 on 2021-06-21 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0010_match_matchid'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='assists1',
            field=models.IntegerField(default=0, verbose_name='assists1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='assists2',
            field=models.IntegerField(default=0, verbose_name='assists2'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='deaths1',
            field=models.IntegerField(default=0, verbose_name='deaths1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='deaths2',
            field=models.IntegerField(default=0, verbose_name='deaths2'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='denies1',
            field=models.IntegerField(default=0, verbose_name='denies1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='denies2',
            field=models.IntegerField(default=0, verbose_name='denies2'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='isVictory',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='kills1',
            field=models.IntegerField(default=0, verbose_name='kills1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='kills2',
            field=models.IntegerField(default=0, verbose_name='kills2'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='lastHits1',
            field=models.IntegerField(default=0, verbose_name='lastHits1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='lastHits2',
            field=models.IntegerField(default=0, verbose_name='lastHits2'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='networth1',
            field=models.IntegerField(default=0, verbose_name='networth1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='match',
            name='networth2',
            field=models.IntegerField(default=0, verbose_name='networth2'),
            preserve_default=False,
        ),
    ]
