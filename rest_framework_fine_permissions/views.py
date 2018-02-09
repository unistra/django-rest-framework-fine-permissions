import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework_fine_permissions.models import FieldPermission,\
                                                   UserFieldPermissions


@staff_member_required
def permissions_export_json(request, ufp_id):
    ufp = get_object_or_404(UserFieldPermissions, pk=ufp_id)
    permissions = {
        'username': ufp.user.username,
        'fields_permissions': [{
            'app_label': permission.content_type.app_label,
            'model': permission.content_type.model,
            'name': permission.name
        } for permission in ufp.permissions.all()]
    }
    return HttpResponse(
        json.dumps(permissions), content_type='application/json')


@staff_member_required
def permissions_import_json(request, ufp_id=0):
    upload_file = request.FILES.get('perms_upload')

    if upload_file:
        try:
            perms = json.loads(upload_file.read().decode('utf-8'))
            username = perms.get('username')

            if ufp_id:
                ufp = get_object_or_404(UserFieldPermissions, pk=ufp_id)
                if username == ufp.user.username:
                    # Clear the old field permissions
                    ufp.permissions.clear()
                else:
                    message = 'The wrong user is defined in the imported file'
                    messages.add_message(request, messages.ERROR, message)
            else:
                user = get_object_or_404(User, username=username)
                ufp = UserFieldPermissions(user=user)
                ufp.save()

            _add_permissions(request, ufp, perms)
            ufp_id = ufp.pk
        except Exception as e:
            message = 'Error in the import : %s' % e
            messages.add_message(request, messages.ERROR, message)
    else:
        message = 'Missing imported file'
        messages.add_message(request, messages.ERROR, message)

    return redirect(
        '/admin/rest_framework_fine_permissions/userfieldpermissions/%s'
        % ufp_id)


def _add_permissions(request, ufp, perms):
    # Create the new field permissions
    fields = perms.get('fields_permissions')
    for field in fields:
        content_type = ContentType.objects.get(
            app_label=field['app_label'], model=field['model'])
        fp = FieldPermission.objects.get_or_create(
            content_type=content_type, name=field['name'])[0]
        ufp.permissions.add(fp)

    message = 'Permissions imported'
    messages.add_message(request, messages.INFO, message)
