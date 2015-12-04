# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'field permission',
                'verbose_name_plural': 'fields permissions',
                'db_table': 'drf_field_permission',
            },
        ),
        migrations.CreateModel(
            name='FilterPermissionModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filter', models.TextField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user filter permission',
                'verbose_name_plural': 'user filters permissions',
                'db_table': 'drf_user_filter_permissions',
            },
        ),
        migrations.CreateModel(
            name='UserFieldPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permissions', models.ManyToManyField(to='rest_framework_fine_permissions.FieldPermission', db_table='drf_user_field_permissions_permission', related_name='user_field_permissions')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user field permission',
                'verbose_name_plural': 'user fields permissions',
                'db_table': 'drf_user_field_permissions',
            },
        ),
        migrations.AlterUniqueTogether(
            name='filterpermissionmodel',
            unique_together=set([('user', 'content_type')]),
        ),
    ]
