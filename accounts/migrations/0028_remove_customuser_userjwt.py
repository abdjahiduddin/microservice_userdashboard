# Generated by Django 2.2.4 on 2019-11-24 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_auto_20190905_1521'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='userjwt',
        ),
    ]
