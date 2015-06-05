from django.db import models


class FieldPermissionManager(models.Manager):

    """ Manage the FieldPermission model. """

    def get_allowed_fields(self, user, model):
        """ Retrieve allowed fields for an authenticated user.

        :param user: an authenticated user
        :type user: django.contrib.auth.models.User
        :param model: a model on which determine allowed fields
        :type model: django.db.models.Model
        :return: a list of fields of the model for the user
        :rtype: django.db.Queryset
        """
        model_name = model.__name__.lower()
        app_label = model._meta.app_label

        return self.filter(
            user_field_permissions__user=user,
            content_type__model=model_name,
            content_type__app_label=app_label
        )
