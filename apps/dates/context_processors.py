# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import re

from django.conf import settings


uppercase = re.compile(r'[A-Z]')


def global_settings(request):
    context = {}
    for k in dir(settings):
        if uppercase.match(k[0]):
            context[k] = getattr(settings, k)
    return context
