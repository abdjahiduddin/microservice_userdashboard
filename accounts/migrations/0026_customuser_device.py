# Generated by Django 2.2.4 on 2019-09-05 15:17

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_remove_customuser_devicemacs'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='device',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
