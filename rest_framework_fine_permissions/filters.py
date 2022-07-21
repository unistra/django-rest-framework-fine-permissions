from rest_framework.filters import BaseFilterBackend
from rest_framework_fine_permissions.serializers import QSerializer
from rest_framework_fine_permissions.models import FilterPermissionModel

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.query import QuerySet


class FilterPermissionBackend(BaseFilterBackend):
    """
    Filter permission backend
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_superuser and not user.is_anonymous and isinstance(queryset, QuerySet):
            try:
                model = queryset.model
                ct = ContentType.objects.get_for_model(model)
                fpm = FilterPermissionModel.objects.get(user=user,
                                                        content_type=ct)
                myfilter = QSerializer(base64=True).loads(fpm.filter)
            except ObjectDoesNotExist:
                myfilter = Q()
            return queryset.filter(myfilter)
        else:
            return queryset
