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

import uuid
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save


class FollowingIntegrityError(ValueError):
    pass


class BlacklistIntegityError(ValueError):
    pass


class Entry(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    total_hours = models.IntegerField(null=True, blank=True)
    start = models.DateField()
    end = models.DateField()
    details = models.TextField(blank=True)

    add_date = models.DateTimeField(default=datetime.datetime.utcnow)
    modify_date = models.DateTimeField(default=datetime.datetime.utcnow,
                                       auto_now=True)

    def __repr__(self):  # pragma: no cover
        return '<Entry: %s, %s - %s>' % (self.user,
                                         self.start,
                                         self.end)


class Hours(models.Model):
    entry = models.ForeignKey(Entry)
    hours = models.IntegerField()
    date = models.DateField()
    birthday = models.BooleanField(default=False)


class BlacklistedUser(models.Model):
    # FIXME: need to figure out the right on_delete here
    observer = models.ForeignKey(User, related_name='observer')
    observable = models.ForeignKey(User, related_name='observable')
    add_date = models.DateTimeField(default=datetime.datetime.utcnow)

    def __repr__(self):  # pragma: no cover
        return '<%s: %r blacklists %r>' % (self.__class__.__name__,
                                           self.observer.username,
                                           self.observable.username)


class FollowingUser(models.Model):
    # FIXME: need to figure out the right on_delete here
    follower = models.ForeignKey(User, related_name='follower')
    following = models.ForeignKey(User, related_name='following')
    add_date = models.DateTimeField(default=datetime.datetime.utcnow)

    def __repr__(self):  # pragma: no cover
        return '<%s: %r follows %r>' % (self.__class__.__name__,
                                           self.follower.username,
                                           self.following.username)


@receiver(post_save, sender=BlacklistedUser)
def blacklist_cleanup_check(sender, instance, **kwargs):
    (FollowingUser.objects
     .filter(follower=instance.observer, following=instance.observable)
     .delete())


@receiver(post_save, sender=FollowingUser)
def follow_cleanup_check(sender, instance, **kwargs):
    (BlacklistedUser.objects
     .filter(observer=instance.follower, observable=instance.following)
     .delete())


@receiver(pre_save, sender=BlacklistedUser)
def blacklist_integrity_check(sender, instance, **kwargs):
    if instance.observer == instance.observable:
        raise BlacklistIntegityError("can't blacklist self")


@receiver(pre_save, sender=FollowingUser)
def following_integrity_check(sender, instance, **kwargs):
    if instance.follower == instance.following:
        raise FollowingIntegrityError("can't follow self")


def generate_random_key(length=None):
    if length is None:
        length = UserKey.KEY_LENGTH
    key = uuid.uuid4().hex[:length]
    while UserKey.objects.filter(key=key).exists():
        key = uuid.uuid4().hex[:length]
    return key


class UserKey(models.Model):

    KEY_LENGTH = 10

    user = models.ForeignKey(User)
    key = models.CharField(max_length=KEY_LENGTH, db_index=True,
                           default=generate_random_key)
    add_date = models.DateTimeField(default=datetime.datetime.utcnow)
