from django.urls import path

from . import views


urlpatterns = [
    # Export permissions
    path('drffp/export/<int:ufp_id>/', views.permissions_export_json, name='drffp-export'),

    # Import permissions
    path('drffp/import/', views.permissions_import_json, name='drffp-import'),
    path('drffp/import/<int:ufp_id>/', views.permissions_import_json, name='drffp-import-ufp'),
]
