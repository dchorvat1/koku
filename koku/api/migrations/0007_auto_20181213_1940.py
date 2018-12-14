# Generated by Django 2.1.2 on 2018-12-13 19:40

from django.db import migrations, models


def migrate_schema_name(apps, schema_editor, model_name):
    Model = apps.get_model('api', model_name)

    for current_model in Model.objects.all():
        cur_schema_name = current_model.schema_name
        newschema_name = cur_schema_name[:cur_schema_name.index('org')]
        current_model.schema_name = newschema_name
        current_model.save()


def migrate_customer_schema_name(apps, schema_editor):
    migrate_schema_name(apps, schema_editor, 'Customer')


def migrate_tenant_schema_name(apps, schema_editor):
    migrate_schema_name(apps, schema_editor, 'Tenant')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_delete_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='account_id',
            field=models.CharField(max_length=150, null=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='customer',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='customer',
            name='org_id',
        ),
        migrations.RunPython(migrate_tenant_schema_name),
        migrations.RunPython(migrate_customer_schema_name)
    ]
