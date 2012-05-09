# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
   url('^login/', views.login, name='users.login'),
   url('^logout/', views.logout, name='users.logout'),
   url('^profile/', views.profile, name='users.profile'),
   url('^debug_org_chart/', views.debug_org_chart,
       name='users.debug_org_chart'),
)
