from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_fine_permissions.urls import urlpatterns as drffp_urls


urlpatterns = drffp_urls
urlpatterns += [
    url(r'^admin/', include(admin.site.urls)),
]
