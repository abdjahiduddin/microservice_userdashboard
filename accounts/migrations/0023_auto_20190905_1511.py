# Generated by Django 2.2.4 on 2019-09-05 15:11

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_customuser_topics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='devicemacs',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='topics',
        ),
        migrations.AddField(
            model_name='customuser',
            name='devicemac',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='customuser',
            name='topic',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
