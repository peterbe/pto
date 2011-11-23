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

import datetime
from django import http
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth import login as auth_login, logout as auth_logout
from dates.models import Entry, Hours
from dates.decorators import json_view
from dates.utils import get_weekday_dates

MOBILE_DATE_FORMAT = '%Y-%m-%d'


def home(request):
    data = {}
    data['page_title'] = 'Mozilla PTO'
    response = render(request, 'mobile/mobile.html', data)
    # if you have loaded this page, forget the no-mobile cookie
    response.delete_cookie('no-mobile')
    return response

@json_view
def right_now(request):
    if not request.user.is_authenticated():  # XXX improve this
        return {'error': 'Not logged in'}
    from dates.views import get_right_nows, get_upcomings
    from dates.helpers import full_name_form, format_date
    right_nows, right_now_users = get_right_nows()
    upcomings, upcoming_users = get_upcomings(14)

    now = []
    for user in right_now_users:
        descriptions = []
        for days_left, entry in right_nows[user]:
            description = 'ends in '
            if days_left == 1:
                description += '1 day '
            else:
                description += '%d days ' % days_left
            description += 'on %s' % format_date(None, entry.end)
            descriptions.append(description)
        now.append({'name': full_name_form(None, user),
                    'descriptions': descriptions})

    upcoming = []
    for user in upcoming_users:
        descriptions = []
        for days, entry in upcomings[user]:
            description = 'starts in '
            if days == 1:
                description += '1 day '
            elif days == 7:
                description += '1 week '
            elif days == 7:
                description += '2 weeks '
            else:
                description += '%d days ' % days
            description += 'on %s' % format_date(None, entry.end)
            descriptions.append(description)
        upcoming.append({'name': full_name_form(None, user),
                    'descriptions': descriptions})

    return {'now': now, 'upcoming': upcoming}


@json_view
def taken(request):
    if not request.user.is_authenticated():  # XXX improve this
        return {'error': 'Not logged in'}
    from dates.views import get_taken_info
    return get_taken_info(request.user)


@csrf_exempt  # XXX fix this
@require_POST
@transaction.commit_on_success
@json_view
def notify(request):
    if not request.user.is_authenticated():  # XXX improve this
        return {'error': 'Not logged in'}
    from dates.forms import AddForm
    from dates.views import clean_unfinished_entries
    form = AddForm(request.user, data=request.POST)
    if form.is_valid():
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']
        details = form.cleaned_data['details'].strip()
        notify = form.cleaned_data['notify']

        entry = Entry.objects.create(
          user=request.user,
          start=start,
          end=end,
          details=details,
        )
        clean_unfinished_entries(entry)
        request.session['notify_extra'] = notify
        return {'entry': entry.pk}
    else:
        return {'form_errors': form.errors}


@csrf_exempt  # XXX fix this
@require_POST
@transaction.commit_on_success
@json_view
def save_hours(request):
    if not request.user.is_authenticated():  # XXX improve this
        return {'error': 'Not logged in'}
    if not request.POST.get('entry'):
        return http.HttpResponseBadRequest("No entry parameter provided")
    try:
        entry = Entry.objects.get(pk=request.POST['entry'])
    except Entry.DoesNotExist:
        return http.HttpResponseNotFound("Not found")
    if entry.user != request.user:
        return http.HttpResponseForbidden("Not your entry")

    from dates.forms import HoursForm
    from dates.views import save_entry_hours, send_email_notification
    form = HoursForm(entry, data=request.POST)
    if form.is_valid():
        total_hours, is_edit = save_entry_hours(entry, form)
        success, email_addresses = send_email_notification(
          entry,
          '',  # extra users to send to
          is_edit=is_edit,
        )
        return {'ok': True}

    else:
        return {'form_errors': form.errors}


@json_view
def hours_json(request):
    if not request.user.is_authenticated():  # XXX improve this
        return {'error': 'Not logged in'}

    entry_id = request.GET.get('entry')
    if not entry_id:
        return {'error': 'No entry pre-loaded'}
    entry = get_object_or_404(Entry, pk=entry_id)
    if entry.user != request.user:
        return http.HttpResponseForbidden("Not your entry")
    days = []

    for date in get_weekday_dates(entry.start, entry.end):
        key = date.strftime('d-%Y%m%d')
        try:
            hours_ = Hours.objects.get(
              date=date,
              entry__user=entry.user,
              hours__gt=0,
            )
            #initial[date.strftime('d-%Y%m%d')] = hours_.hours
            value = hours_.hours
        except Hours.DoesNotExist:
            #initial[date.strftime('d-%Y%m%d')] = settings.WORK_DAY
            value = settings.WORK_DAY
        days.append({'key': key,
                     'value': value,
                     'full_day': date.strftime(settings.DEFAULT_DATE_FORMAT)})
    return days

@json_view
def settings_json(request):
    if not request.user.is_authenticated():  # XXX improve this
        return {'error': 'Not logged in'}

    data = {
      'username': request.user.username,
      'email': request.user.email,
    }
    from dates.helpers import full_name_form
    data['full_name'] = full_name_form(None, request.user)
    profile = request.user.get_profile()
    if profile.start_date:
        data['start_date'] = profile.start_date.strftime(
          MOBILE_DATE_FORMAT)
    if profile.country:
        data['country'] = profile.country
    if profile.city:
        data['city'] = profile.city

    return data

@csrf_exempt  # XXX fix this
@require_POST
@transaction.commit_on_success
@json_view
def save_settings(request):
    if not request.user.is_authenticated():  # XXX improve this
        return {'error': 'Not logged in'}
    from users.forms import ProfileForm
    profile = request.user.get_profile()
    form = ProfileForm(instance=profile, data=request.POST)
    if form.is_valid():
        profile = form.save(commit=False)
        profile.country = form.cleaned_data['country']
        profile.save()
        return {'ok': True}
    else:
        return {'form_errors': form.errors}


def exit_mobile(request):
    r = redirect('/')
    then = datetime.datetime.now() + datetime.timedelta(days=300)
    r.set_cookie('no-mobile', 1, expires=then)
    return r


@csrf_exempt  # XXX fix this
@json_view
def login(request):
    if request.method == 'GET':
        return {'logged_in': request.user.is_authenticated()}

    from users.forms import AuthenticationForm
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        return {'ok': True}
    else:
        return {'form_errors': form.errors}

@csrf_exempt  # XXX fix this
@require_POST
@json_view
def logout(request):
    auth_logout(request)
    return {'ok': True}
