# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.


from django.conf import settings


class UnrecognizedCountryError(ValueError):
    pass


def get_country_totals(country):
    if country in settings.TOTALS:
        return settings.TOTALS[country]
    raise UnrecognizedCountryError(country)
