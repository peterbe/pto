# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='mobile.home'),
    url(r'^cache.appcache$', views.appcache, name='mobile.appcache'),
    url(r'^rightnow.json$', views.right_now, name='mobile.right_now'),
    url(r'^taken.json$', views.taken, name='mobile.taken'),
    url(r'^settings.json$', views.settings_json, name='mobile.settings'),
    url(r'^settings/$', views.save_settings, name='mobile.save_settings'),
    url(r'^notify/$', views.notify, name='mobile.notify'),
    url(r'^hours.json$', views.hours_json, name='mobile.hours'),
    url(r'^hours/$', views.save_hours, name='mobile.save_hours'),
    url(r'^exit/$', views.exit_mobile, name='mobile.exit'),
    url(r'^login/$', views.login, name='mobile.login'),
    url(r'^logout/$', views.logout, name='mobile.logout'),
)
