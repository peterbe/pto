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
# The Original Code is Mozilla Sheriff Duty.
#
# The Initial Developer of the Original Code is Mozilla Corporation.
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#    Peter Bengtsson <peterbe@mozilla.com>
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

import logging
from django import http
from django.shortcuts import redirect, render
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.db import transaction
import django.contrib.auth.views
from django.conf import settings
from session_csrf import anonymous_csrf
import forms
from models import get_user_profile
from dates.decorators import json_view
from utils import ldap_lookup


@anonymous_csrf
def login(request):
    # mostly copied from zamboni
    logout(request)

    #from monkeypatch_template_engine import jinja_for_django as jfd
    #django.contrib.auth.views.render_to_response = jfd
    r = django.contrib.auth.views.login(request,
                         template_name='users/login.html',
                         redirect_field_name=REDIRECT_FIELD_NAME,
                         authentication_form=forms.AuthenticationForm)

    if isinstance(r, http.HttpResponseRedirect):
        # Succsesful log in according to django. Now we do our checks. I do
        # the checks here instead of the form's clean() because I want to use
        # the messages framework and it's not available in the request there
        user = get_user_profile(request.user)
        rememberme = request.POST.get('rememberme', None)
        if rememberme:
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            logging.debug((u'User (%s) logged in successfully with '
                                        '"remember me" set') % user)

    return r


def logout(request):
    django.contrib.auth.logout(request)
    #if 'to' in request.GET:
    #    request = _clean_next_url(request)
    next = request.GET.get('next') or settings.LOGOUT_REDIRECT_URL
    response = http.HttpResponseRedirect(next)
    return response




@transaction.commit_on_success
@login_required
def profile(request):
    profile = request.user.get_profile()
    data = {}
    if request.method == 'POST':
        form = forms.ProfileForm(instance=profile, data=request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            country = form.cleaned_data['country']
            profile.city = city
            profile.country = country
            profile.save()

            return redirect('/')
    else:
        form = forms.ProfileForm(instance=profile)

    data['form'] = form
    return render(request, 'users/profile.html', data)


@login_required
def debug_org_chart(request):  # pragma: no cover
    if not settings.DEBUG:
        return http.HttpResponseForbidden('only in debug mode')

    parents = {}
    from collections import defaultdict
    from .models import UserProfile
    top = []
    childen = defaultdict(list)
    for profile in UserProfile.objects.all():
        user = profile.user
        if profile.manager_user:
            parents[user] = profile.manager_user
            childen[profile.manager_user].append(user)
        else:
            top.append(user)


    def _structure(node, indentation=0):
        items = []
        for child in childen[node]:
            items.append((child, _structure(child, indentation=indentation+1)))
        return items

    all = []
    for each in top:
        all.append((each, _structure(each)))

    html = []
    def _render(user, sublist, indentation=0):
        html.append("<li>" + user.username)
        if sublist:
            html.append("<ul>")
            for subuser, subsublist in sublist:
                _render(subuser, subsublist)
            html.append("</ul>")
        html.append("</li>")
    for user, sublist in all:
        html.append("<ul>")
        _render(user, sublist)
        html.append("</ul>")

    return http.HttpResponse('\n'.join(html))
