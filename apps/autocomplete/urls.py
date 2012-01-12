# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^cities/$', views.cities, name='autocomplete.cities'),
    url(r'^users/$', views.users, name='autocomplete.users'),
    url(r'^users/knownonly/$', views.users,
      {'known_only': True},
      name='autocomplete.users_known_only'),
)
