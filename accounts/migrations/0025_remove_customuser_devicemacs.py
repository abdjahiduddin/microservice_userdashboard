# Generated by Django 2.2.4 on 2019-09-05 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_auto_20190905_1512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='devicemacs',
        ),
    ]
