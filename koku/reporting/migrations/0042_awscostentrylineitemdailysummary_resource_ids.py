# Generated by Django 2.1.5 on 2019-02-27 14:52

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0041_auto_20190301_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='awscostentrylineitemdailysummary',
            name='resource_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), null=True, size=None),
        ),
    ]
