# Generated by Django 2.2.4 on 2019-09-05 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20190905_1306'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='devicemacs',
            new_name='topics_devicemacs_jwts',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='topics',
        ),
    ]
