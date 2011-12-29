# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
# 
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
# 
# The Initial Developer of the Original Code is Mozilla Corporation.
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
# 
# Contributor(s):
#   Peter Bengtsson <peterbe@mozilla.com>
# 
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
# 
# ***** END LICENSE BLOCK *****

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
)
