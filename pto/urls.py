from django.conf import settings
from django.conf.urls.defaults import patterns, include

from django.contrib import admin
admin.autodiscover()

from funfactory.monkeypatches import patch
patch()

handler500 = 'apps.dates.views.handler500'

urlpatterns = patterns('',
    (r'^users/', include('apps.users.urls')),
    (r'^mobile/', include('apps.mobile.urls')),
    (r'^autocomplete/', include('apps.autocomplete.urls')),
    (r'', include('apps.dates.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
