# Generated by Django 2.2.4 on 2019-09-05 14:44

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_auto_20190905_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='topics',
            field=jsonfield.fields.JSONField(blank=True, default=dict),
        ),
    ]
