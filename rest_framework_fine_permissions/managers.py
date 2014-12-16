from django.db.models import Manager
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from rest_framework_fine_permissions.serializers import QSerializer
from rest_framework_fine_permissions.models import FilterPermissionModel


class FilterPermissionManager(Manager):
    """
    manager for field permission
    """

    def __init__(self, user, model):
        super().__init__()
        self.user = user
        self.model = model

    def get_queryset(self):
        myfilter = Q()

        if not self.user.is_superuser:
            try:
                ct = ContentType.objects.get_for_model(self.model)
                fpm = FilterPermissionModel.objects.get(user=self.user,
                                                        content_type=ct)
                myfilter = QSerializer().loads(fpm.filter)
            except ObjectDoesNotExist:
                pass

        return super().get_queryset().filter(myfilter)
