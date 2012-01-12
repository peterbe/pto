# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib import admin
from models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):  # pragma: no cover
    list_display = ('user_display', 'hr_manager', 'city', 'country',
                    'manager_user_display')
    list_filter = ('hr_manager',)

    def _show_name(self, user):
        name = ('%s %s' % (user.first_name, user.last_name)).strip()
        if not name:
            name = user.username
        if user.email:
            name += ' <%s>' % user.email
        return name

    def user_display(self, obj):
        return self._show_name(obj.user)
    user_display.short_description = "User"

    def manager_user_display(self, obj):
        if obj.manager_user:
            return self._show_name(obj.manager_user)
        else:
            return 'none'
    manager_user_display.short_description = "Manager"


admin.site.register(UserProfile, UserProfileAdmin)
