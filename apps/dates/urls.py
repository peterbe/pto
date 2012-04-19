# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='dates.home'),
    url(r'^notify/$', views.notify, name='dates.notify'),
    url(r'^notify/cancel/$', views.cancel_notify, name='dates.cancel_notify'),
    url(r'^(?P<pk>\d+)/hours/$', views.hours, name='dates.hours'),
    url(r'^(?P<pk>\d+)/sent/$', views.emails_sent, name='dates.emails_sent'),
    url(r'^list/$', views.list_, name='dates.list'),
    url(r'^list/csv/$', views.list_csv, name='dates.list_csv'),
    url(r'^list/json/$', views.list_json, name='dates.list_json'),
    url(r'^calendar/events/$', views.calendar_events,
        name='dates.calendar_events'),
    url(r'^following/$', views.following, name='dates.following'),
    url(r'^following/save/$', views.save_following, name='dates.save_following'),
    url(r'^following/save/unfollow/$', views.save_unfollowing, name='dates.save_unfollowing'),
    url(r'^(?P<key>\w{10})/ptocalendar\.ics$', views.calendar_vcal, name='dates.calendar_vcal'),
    url(r'^reset-calendar-url$', views.reset_calendar_url, name='dates.reset_calendar_url'),
    url(r'^about-calendar-url$', views.about_calendar_url, name='dates.about_calendar_url'),
    url(r'^duplicate-report/$', views.duplicate_report, name='dates.duplicate_report'),
)
