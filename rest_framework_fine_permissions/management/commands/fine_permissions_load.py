#!/usr/bin/env python

from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from rest_framework_fine_permissions.models import UserFieldPermissions, FieldPermission
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import json
from optparse import make_option
import sys
from django.contrib.contenttypes.models import ContentType



class Command(BaseCommand):

    help = ("Loads the user's fieds permissions into the database from a fixture of the given user ")
    args = 'json file'


    option_list = BaseCommand.option_list + (
        make_option('-u', '--user', help='Specify another user'),
    )

    def handle(self, *args, **options):
        """
        dump fields permissions for a user
        """

        def get_user(username):
            try:
                return User.objects.get(username=username)
            except ObjectDoesNotExist as e:
                raise CommandError("This user doesn't exist in the database")

        def add_permissions(user_field_permissions, content_type, name):

            p = None
            try:
                p = FieldPermission.objects.get(content_type=content_type, name=name)
            except ObjectDoesNotExist:
                p = FieldPermission(content_type=content_type, name=name)
                p.save()
            finally:
                user_field_permissions.permissions.add(p)



        if len(args) !=1:
             raise CommandError("Specifies a json file created by the fine_permissions_dump command")
        else:
            try:


                with open(args[0], 'r') as json_file:
                    myjson = json.load(json_file)

                    user = get_user(options.get('user')) if options['user'] else get_user(myjson['username'])
                    fields_permissions = myjson['fields_permissions']

                    user_field_permissions = UserFieldPermissions(user=user)
                    user_field_permissions.save()

                    for f in fields_permissions:
                        content_type = ContentType.objects.get(app_label=f["app_label"], model=f["model"])
                        add_permissions(user_field_permissions, content_type, f['name'])


            except Exception as e:
                raise CommandError(e)

