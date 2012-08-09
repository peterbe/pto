# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
from django.conf import settings
from .models import Entry, Hours, BlacklistedUser, FollowingUser, UserKey
from .utils.countrytotals import UnrecognizedCountryError, get_country_totals
from pto.apps.users.models import UserProfile, User


def get_taken_info(user):
    data = {}

    profile = user.get_profile()
    if profile.country:
        data['country'] = profile.country
        try:
            data['country_totals'] = get_country_totals(profile.country)
        except UnrecognizedCountryError:
            data['unrecognized_country'] = True

    today = datetime.date.today()
    start_date = datetime.date(today.year, 1, 1)
    last_date = datetime.date(today.year + 1, 1, 1)
    from django.db.models import Sum
    qs = Entry.objects.filter(
      user=user,
      start__gte=start_date,
      end__lt=last_date
    )
    agg = qs.aggregate(Sum('total_hours'))
    total_hours = agg['total_hours__sum']
    if total_hours is None:
        total_hours = 0
    data['taken'] = _friendly_format_hours(total_hours)

    return data


def _friendly_format_hours(total_hours):
    days = 1.0 * total_hours / settings.WORK_DAY
    hours = total_hours % settings.WORK_DAY

    if not total_hours:
        return '0 days'
    elif total_hours < settings.WORK_DAY:
        return '%s hours' % total_hours
    elif total_hours == settings.WORK_DAY:
        return '1 day'
    else:
        if not hours:
            return '%d days' % days
        else:
            return '%s days' % days


def get_minions(user, depth=1, max_depth=2):
    minions = []
    for minion in (UserProfile.objects.filter(manager_user=user)
                   .select_related('manager_user')
                   .order_by('manager_user')):
        minions.append(minion.user)

        if depth < max_depth:
            minions.extend(get_minions(minion.user,
                                       depth=depth + 1,
                                       max_depth=max_depth))
    return minions


def get_siblings(user):
    profile = user.get_profile()
    if not profile.manager_user:
        return []
    users = []
    for profile in (UserProfile.objects
                    .filter(manager_user=profile.manager_user)
                    .exclude(pk=user.pk)
                    .select_related('user')):
        users.append(profile.user)
    return users


def get_followed_users(user):
    users = []
    for each in (FollowingUser.objects
                 .filter(follower=user)
                 .select_related('following')):
        users.append(each.following)
    return users


def get_following_users(user):
    users = []
    for each in (FollowingUser.objects
                 .filter(following=user)
                 .select_related('follower')):
        users.append(each.follower)
    return users


def get_observed_users(this_user, depth=1, max_depth=2):
    """return a list of the users that this user FOLLOWS. Direct or
    in-direct.

    E.g her minions, her peers, her manager, her deliberate followings, etc
    """
    users = []

    def is_blacklisted(user):
        # XXX this can be optimized by pulling down the entire list once first
        return (BlacklistedUser.objects
                .filter(observer=this_user, observable=user)
                .exists())

    for user in get_minions(this_user, depth=depth, max_depth=max_depth):
        if user not in users:
            if not is_blacklisted(user):
                users.append(user)

    for user in get_siblings(this_user):
        if user not in users:
            if not is_blacklisted(user):
                users.append(user)

    profile = this_user.get_profile()
    manager = profile.manager_user
    if manager and manager not in users:
        if not is_blacklisted(manager):
            users.append(manager)

    for user in get_followed_users(this_user):
        if user not in users:
            users.append(user)

    return users


def get_observing_users(this_user, depth=1, max_depth=2):
    """return a list of the users that his user is FOLLOWED BY. Direct or
    in-direct.

    E.g. her peers, her manager, her peers, her deliberate followers etc.
    """
    if max_depth > 2:  # pragma: no cover
        raise NotImplementedError("Feature not implemented yet")

    def is_blacklisted(user):
        # XXX this can be optimized by pulling down the entire list once first
        return (BlacklistedUser.objects
                .filter(observer=user, observable=this_user)
                .exists())

    users = []
    for user in get_minions(this_user, depth=depth, max_depth=1):
        if user not in users:
            if not is_blacklisted(user):
                users.append(user)

    for user in get_siblings(this_user):
        if user not in users:
            if not is_blacklisted(user):
                users.append(user)

    profile = this_user.get_profile()
    manager = profile.manager_user
    if manager:
        if manager not in users:
            if not is_blacklisted(manager):
                users.append(manager)
        if max_depth >= 2:
            manager_profile = manager.get_profile()
            manager_manager = manager_profile.manager_user
            if manager_manager:
                if manager_manager not in users:
                    users.append(manager_manager)

    for user in get_following_users(this_user):
        if user not in users:
            users.append(user)

    return users
