# Generated by Django 2.2.4 on 2019-09-05 03:42

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20190901_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='devicemac',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
