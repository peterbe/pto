# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import uuid
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings


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

    @property
    def total_days(self):
        days = self.total_hours / settings.WORK_DAY
        if self.total_hours % settings.WORK_DAY:
            days += 0.5
        return days


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

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.key)
