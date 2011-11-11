from django.conf import settings
from django.conf.urls.defaults import patterns, include

from django.contrib import admin
admin.autodiscover()

handler500 = 'dates.views.handler500'

urlpatterns = patterns('',
    (r'^users/', include('users.urls')),
    (r'^mobile/', include('mobile.urls')),
    (r'', include('dates.urls')),

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

## Monkey patches

# Monkey-patch django forms to avoid having to use Jinja2's |safe everywhere.
import safe_django_forms
safe_django_forms.monkeypatch()

# Monkey-patch Django's csrf_protect decorator to use session-based CSRF
# tokens:
if 'session_csrf' in settings.INSTALLED_APPS:
    import session_csrf
    session_csrf.monkeypatch()
