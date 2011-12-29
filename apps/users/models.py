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

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def valid_email(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False


def get_user_profile(user):
    try:
        return user.get_profile()
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(user=user)


@receiver(post_save, sender=User)
def force_profile_creation(sender, instance, **kwargs):
    # django-auth-ldap needs to to map stuff like 'manager' and 'office'
    get_user_profile(instance)


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    manager = models.CharField(max_length=100, blank=True)
    manager_user = models.ForeignKey(User, blank=True, null=True,
                                     on_delete=models.SET_NULL,
                                     related_name='manager_user')
    start_date = models.DateField(blank=True, null=True)
    office = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    hr_manager = models.BooleanField(default=False)

    def __repr__(self):  # pragma: no cover
        return "<UserProfile: %s>" % self.user


@receiver(pre_save, sender=UserProfile)
def explode_office_to_country_and_city(sender, instance, **kwargs):
    if instance.office and ':::' in instance.office:
        city, country = instance.office.split(':::')
        instance.city = city
        instance.country = country


@receiver(pre_save, sender=UserProfile)
def explode_find_manager_user(sender, instance, **kwargs):
    if instance.manager and valid_email(instance.manager):
        for user in User.objects.filter(email__iexact=instance.manager):
            instance.manager_user = user
