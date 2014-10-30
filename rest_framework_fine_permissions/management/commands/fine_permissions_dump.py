#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
from rest_framework_fine_permissions.models import UserFieldPermissions
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import json


class Command(BaseCommand):

    help = ("Output the user's fieds permissions of the database as a fixture of the given user ")
    args = 'user'

    def handle(self, *args, **options):
        """
        dump fields permissions for a user
        """

        def get_user(username):
            try:
                return User.objects.get(username=username)
            except ObjectDoesNotExist as e:
                raise CommandError("This user doesn't exist in the database")

        def get_fields_permissions(user):
            try:
                return UserFieldPermissions.objects.get(user=user)
            except ObjectDoesNotExist as e:
                raise CommandError("This user doesn't have fields permissions")



        if len(args) !=1:
            raise CommandError("Specifies a user")
        else:
            try:
                self.stdout.ending = None
                user = get_user(args[0])
                fields_permissions  = get_fields_permissions(user)
                permissions = fields_permissions.permissions.all()

                jsoneatthat = {'username': user.username, 
                    'fields_permissions' : [ {'app_label': permission.content_type.app_label, 'model' : permission.content_type.model, 'name': permission.name } for permission in permissions]}

                self.stdout.write(json.dumps(jsoneatthat))

            except:
                raise

