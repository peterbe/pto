from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='mobile.home'),
    url(r'^rightnow.json$', views.right_now, name='mobile.right_now'),
    url(r'^left.json$', views.left, name='mobile.left'),
    url(r'^settings.json$', views.settings_json, name='mobile.settings'),
    url(r'^settings/$', views.save_settings, name='mobile.save_settings'),
    url(r'^notify/$', views.notify, name='mobile.notify'),
    url(r'^hours.json$', views.hours_json, name='mobile.hours'),
    url(r'^exit/$', views.exit_mobile, name='mobile.exit'),
)
