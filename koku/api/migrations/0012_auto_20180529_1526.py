# Generated by Django 2.0.5 on 2018-05-29 15:26

from django.contrib.auth.hashers import make_password
from django.db import migrations

from koku.env import ENVIRONMENT


def create_service_admin(apps, schema_editor):
    """Create the Service Admin."""
    User = apps.get_model('api', 'User')

    service_email = ENVIRONMENT.get_value('SERVICE_ADMIN_EMAIL',
                                              default='admin@example.com')
    service_user = ENVIRONMENT.get_value('SERVICE_ADMIN_USER',
                                            default='admin')
    service_pass = ENVIRONMENT.get_value('SERVICE_ADMIN_PASSWORD',
                                            default='pass')

    User.objects.get_or_create(
        username=service_user,
        email=service_email,
        password=make_password(service_pass),
        is_superuser=True,
        is_staff=True
    )


def create_public_schema(apps, schema_editor):
    """Get or create a tenant for the public schema."""
    Tenant = apps.get_model('api', 'Tenant')

    Tenant.objects.get_or_create(schema_name='public')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20180524_1838'),
    ]

    operations = [
        migrations.RunPython(create_service_admin),
        migrations.RunPython(create_public_schema),
    ]