from rest_framework_fine_permissions.urls import urlpatterns as drffp_urls

from django.contrib import admin
from django.urls import path

urlpatterns = drffp_urls
urlpatterns += [
    path('admin/', admin.site.urls),
]
