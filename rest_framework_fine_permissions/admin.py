# -*- coding: utf-8 -*-

"""
"""

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType


from .models import FieldPermission, UserFieldPermissions
from .utils import get_field_permissions


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
        choice_str = lambda app, model, sep:\
            '{0[0]}{1}{0[1]}{1}{2}'.format(app.split('.'), sep, model)
        choices = []
        for model, fields in get_field_permissions().items():
            choices += [(choice_str(model, field, '.'), choice_str(model, field, ' | '))
                        for field in fields]
        self.fields['permissions'].choices = sorted(choices)

        # Initial datas
        instance = kwargs.get('instance')
        if instance:
            fps = ['.'.join(fp) for fp in instance.permissions.all()
                   .values_list(
                        'content_type__app_label',
                        'content_type__model',
                        'name'
                    )
            ]
            self.initial['permissions'] = fps

    def save(self, commit=True):
        form = super(UserFieldPermissionsForm, self).save(commit=False)
        cleaned = self.cleaned_data

        field_permissions = []
        for permission in cleaned['permissions']:
            app_label, model_name, field = permission.split('.')
            ct = ContentType.objects.get_by_natural_key(app_label, model_name)
            fp = FieldPermission.objects.get_or_create(
                content_type=ct,
                name=field
            )[0]
            field_permissions.append(fp.pk)

        self.cleaned_data['permissions'] = field_permissions

        if commit:
            form.save()
            form.save_m2m()

        return form


class UserFieldPermissionsAdmin(admin.ModelAdmin):

    """
    """
    list_display = ('user', )
    form = UserFieldPermissionsForm

admin.site.register(UserFieldPermissions, UserFieldPermissionsAdmin)
