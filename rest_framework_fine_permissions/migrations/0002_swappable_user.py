# Generated by Django 3.0.8 on 2020-09-16 10:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_framework_fine_permissions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='UserFieldPermissions',
            name='user',
            field=models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            )
        ),
        migrations.AlterField(
            model_name='FilterPermissionModel',
            name='user',
            field=models.ForeignKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            )
        ),
    ]
