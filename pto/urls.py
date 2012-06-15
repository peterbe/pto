from django.conf import settings
from django.conf.urls.defaults import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from funfactory.monkeypatches import patch
patch()

handler500 = 'pto.apps.dates.views.handler500'

urlpatterns = patterns('',
    (r'^users/', include('pto.apps.users.urls')),
    (r'^mobile/', include('pto.apps.mobile.urls')),
    (r'^autocomplete/', include('pto.apps.autocomplete.urls')),
    (r'', include('pto.apps.dates.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
