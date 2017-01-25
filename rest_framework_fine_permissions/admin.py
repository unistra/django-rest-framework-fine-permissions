# -*- coding: utf-8 -*-

"""
"""

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q
from django.utils.html import format_html

from .fields import ModelPermissionsField
from .models import FieldPermission, UserFieldPermissions, FilterPermissionModel
from .utils import get_field_permissions
from .serializers import QSerializer


class UserFieldPermissionsForm(forms.ModelForm):

    """
    """

    permissions = forms.MultipleChoiceField(
        widget=FilteredSelectMultiple(
            verbose_name='User field permissions',
            is_stacked=False,
        )
    )

    class Meta:
        model = UserFieldPermissions
        exclude = ('content_type',)

    def __init__(self, *args, **kwargs):
        super(UserFieldPermissionsForm, self).__init__(*args, **kwargs)

        # Choices
        def choice_str(model, field, sep):
            return '{model[0]}{sep}{model[1]}{sep}{field}'\
                .format(model=model.split('.'), field=field, sep=sep)

        choices = []
        self.field_permissions = get_field_permissions()
        self.field_serializers = {}

        for model, values in self.field_permissions.items():
            fields, ser = values
            choices += [(choice_str(model, field, '.'), choice_str(model, field, ' | '))
                        for field in fields]
            self.field_serializers.update({choice_str(model, field, '.'): ser for field in fields})
        self.fields['permissions'].choices = sorted(choices)

        # Initial datas
        instance = kwargs.get('instance')
        if instance:
            fps = ['.'.join(fp) for fp in instance.permissions.all()
                   .values_list(
                        'content_type__app_label',
                        'content_type__model',
                        'name'
                    )]
            self.initial['permissions'] = fps

    def clean(self):
        cleaned = self.cleaned_data
        field_permissions = []
        model_perms = {}
        conflicts = []

        for permission in cleaned['permissions']:
            app_label, model_name, field_name = permission.split('.')
            ct = ContentType.objects.get_by_natural_key(app_label, model_name)
            fp = FieldPermission.objects.get_or_create(
                content_type=ct,
                name=field_name
            )[0]
            field_permissions.append(fp.pk)

            # Check for each added permission if there is a recursive call
            # between two ModelPermissionsField fields
            app = '%s.%s' % (app_label, model_name)
            values = self.field_permissions.get(app)
            fields = values[0] if values else []

            if field_name in fields:
                field = self.field_permissions.get(app)
                field = field[0][field_name] if field else None

                if isinstance(field, ModelPermissionsField):
                    name = '{0.__module__}.{0.__name__}'.format(field.serializer)
                    model_perms[self.field_serializers[permission]] = permission

                    if name in model_perms:
                        conflicts.append(
                            '<li><b>%s</b> and <b>%s</b></li>'
                            % (permission, model_perms[name]))

        if conflicts:
            msg = 'Recursive ModelPermissionsField call between<ul>{}</ul>'\
                .format(''.join(conflicts))
            raise forms.ValidationError(format_html(msg))

        self.cleaned_data['permissions'] = field_permissions


class UserFieldPermissionsAdmin(admin.ModelAdmin):

    """
    """
    list_display = ('user', )
    form = UserFieldPermissionsForm


class ContentTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s | %s" % (obj.app_label, obj.model)


class UserFilterPermissionsForm(forms.ModelForm):
    """
    filter permissions form
    """

    current_filter = forms.CharField(required=False)
    content_type = ContentTypeChoiceField(queryset=ContentType.objects.all().order_by('app_label', 'model'))

    class Meta:
        model = FilterPermissionModel
        exclude = []

    def __init__(self, *args, **kwargs):
        form = super(UserFilterPermissionsForm, self).__init__(*args, **kwargs)

        # Initial datas
        instance = kwargs.get('instance')
        self.fields['current_filter'].widget.attrs['readonly'] = True
        self.fields['current_filter'].widget.attrs['size'] = 130

        if instance:
            myq = QSerializer(base64=True).loads(instance.filter)
            current_filter = myq.__str__()
        else:
            myq = Q(myfield="myvalue")
            current_filter = ""

        self.initial['current_filter'] = current_filter
        self.initial['filter'] = QSerializer().dumps(myq)

        self.fields['filter'].widget.attrs['rows'] = len(self.initial['filter'].splitlines()) + 4

    def clean_filter(self):
        data = self.cleaned_data['filter']
        if data:
            try:
                myq = QSerializer().loads(data)
            except:
                raise forms.ValidationError("filter is not a valid entry for a q object !")
            else:
                if isinstance(myq, Q):
                    data = QSerializer(base64=True).dumps(myq)
                else:
                    raise forms.ValidationError("filter is not a q object !")

        return data

    def save(self, commit=True):
        form = super(UserFilterPermissionsForm, self).save(commit=False)

        if commit:
            form.save()
            form.save_m2m()

        return form


class UserFilterPermissionsAdmin(admin.ModelAdmin):
    """
    filter permissions admin
    """
    list_display = ('user', 'content_type')
    form = UserFilterPermissionsForm


admin.site.register(UserFieldPermissions, UserFieldPermissionsAdmin)
admin.site.register(FilterPermissionModel, UserFilterPermissionsAdmin)
