from django.conf.urls import url

from . import views

urlpatterns = [
    # Export permissions
    url(r'^drffp/export/(?P<ufp_id>\d+)/$', views.permissions_export_json, name='drffp-export'),

    # Import permissions
    url(r'^drffp/import/$', views.permissions_import_json, name='drffp-import'),
    url(r'^drffp/import/(?P<ufp_id>\d+)/$', views.permissions_import_json, name='drffp-import-ufp'),
]
