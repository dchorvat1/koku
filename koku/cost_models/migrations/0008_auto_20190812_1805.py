# Generated by Django 2.2.4 on 2019-08-12 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cost_models', '0007_auto_20190613_0057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costmodel',
            name='source_type',
            field=models.CharField(choices=[('AWS', 'AWS'), ('OCP', 'OCP'), ('AZURE', 'AZURE')], max_length=50),
        ),
    ]
