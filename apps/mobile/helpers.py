from django.conf import settings
import jinja2
from jingo import register


@register.function
@jinja2.contextfunction
def bundle_list_css(context, bundle, build_id=None):
    url = settings.MEDIA_URL
    url += 'css/%s-min.css' % bundle
    if build_id:
        url += '?build=%s' % build_id
    return url

@register.function
@jinja2.contextfunction
def bundle_list_js(context, bundle, build_id=None):
    url = settings.MEDIA_URL
    url += 'js/%s-min.js' % bundle
    if build_id:
        url += '?build=%s' % build_id
    return url
