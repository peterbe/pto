# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
from django import http
from django.shortcuts import redirect, render
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.contrib import messages
import django.contrib.auth.views
from session_csrf import anonymous_csrf
import forms
from models import get_user_profile


@anonymous_csrf
def login(request):
    # mostly copied from zamboni
    logout(request)

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
            if city and country:
                profile.office = '%s:::%s' % (city, country)
            profile.save()

            messages.info(request,
              'Profile details saved'
            )
            return redirect('/')
    else:
        # 'country' is a custom field in the ProfileForm class
        # so send that separately
        form = forms.ProfileForm(instance=profile,
                                 initial={'country': profile.country})

    data['form'] = form
    return render(request, 'users/profile.html', data)


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
            items.append((child,
                          _structure(child, indentation=indentation + 1)))
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
