# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import ldap
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import simplejson as json
from users.utils.ldap_mock import MockLDAP
from mock import Mock
from nose.tools import eq_, ok_
from test_utils import TestCase


class CitiesTest(TestCase):

    def test_cities(self):
        url = reverse('autocomplete.cities')
        response = self.client.get(url)
        eq_(response.status_code, 403)

        mortal = User.objects.create(username='mortal')
        mortal.set_password('secret')
        mortal.save()
        assert self.client.login(username='mortal', password='secret')

        response = self.client.get(url)
        eq_(response.status_code, 200)
        ok_(response['content-type'].startswith('application/json'))
        struct = json.loads(response.content)
        eq_(struct, [])

        profile = mortal.get_profile()
        profile.city = 'London'
        profile.save()

        response = self.client.get(url)
        eq_(response.status_code, 200)
        struct = json.loads(response.content)
        eq_(struct, ['London'])

        bob = User.objects.create(username='bob')
        profile = bob.get_profile()
        profile.city = 'Aberdeen'
        profile.save()

        response = self.client.get(url)
        eq_(response.status_code, 200)
        struct = json.loads(response.content)
        eq_(struct, ['Aberdeen', 'London'])

        response = self.client.get(url, {'term': 'LON'})
        eq_(response.status_code, 200)
        struct = json.loads(response.content)
        eq_(struct, ['London'])


class UsersTest(TestCase):

    def setUp(self):
        super(UsersTest, self).setUp()

        ldap.open = Mock('ldap.open')
        ldap.open.mock_returns = Mock('ldap_connection')
        ldap.set_option = Mock(return_value=None)

    def test_users(self):
        results = [
          ('mail=peter@mozilla.com,o=com,dc=mozilla',
           {'cn': ['Peter Bengtsson'],
            'givenName': ['Pet\xc3\xa3r'], # utf-8 encoded
            'mail': ['peterbe@mozilla.com'],
            'sn': ['Bengtss\xc2\xa2n'],
            'uid': ['pbengtsson']
            })
        ]

        ldap.initialize = Mock(return_value=MockLDAP({
          '(&(objectClass=inetOrgPerson)(mail=*)(|(mail=peter*)(givenName=peter*)(sn=peter*)))': results
        }))

        url = reverse('autocomplete.users')
        response = self.client.get(url, {'term': '  i  '})
        eq_(response.status_code, 403)

        mortal = User.objects.create(
          username='mortal',
          first_name='Mortal',
          last_name='Joe'
        )
        mortal.set_password('secret')
        mortal.save()
        assert self.client.login(username='mortal', password='secret')

        response = self.client.get(url, {'term': '  i  '})
        eq_(response.status_code, 200)
        ok_(response['content-type'].startswith('application/json'))

        response = self.client.get(url, {'term': 'peter'})
        eq_(response.status_code, 200)
        ok_(response['content-type'].startswith('application/json'))
        struct = json.loads(response.content)
        ok_(isinstance(struct, list))
        first_item = struct[0]

        label = '%s %s <%s>' % (u'Pet\xe3r',
                                u'Bengtss\xa2n',
                                'peterbe@mozilla.com')
        value = label
        eq_(first_item, {
          'id': 'pbengtsson',
          'label': label,
          'value': value,
        })

    def test_users_knownonly(self):
        results = [
          ('mail=peter@mozilla.com,o=com,dc=mozilla',
           {'cn': ['Peter Bengtsson'],
            'givenName': ['Pet\xc3\xa3r'], # utf-8 encoded
            'mail': ['peterbe@mozilla.com'],
            'sn': ['Bengtss\xc2\xa2n'],
            'uid': ['pbengtsson']
            }),
          ('mail=peterino@mozilla.com,o=com,dc=mozilla',
           {'cn': ['Peterino Gaudy'],
            'givenName': ['Pet\xc3\xa3rino'], # utf-8 encoded
            'mail': ['peterino@mozilla.com'],
            'sn': ['Gaudi'],
            'uid': ['peterino']
            }),
        ]

        ldap.initialize = Mock(return_value=MockLDAP({
          '(&(objectClass=inetOrgPerson)(mail=*)(|(mail=peter*)(givenName=peter*)(sn=peter*)))': results
        }))

        url = reverse('autocomplete.users_known_only')

        mortal = User.objects.create(
          username='mortal',
          first_name='Mortal',
          last_name='Joe'
        )
        mortal.set_password('secret')
        mortal.save()
        assert self.client.login(username='mortal', password='secret')

        response = self.client.get(url, {'term': 'peter'})
        eq_(response.status_code, 200)
        ok_(response['content-type'].startswith('application/json'))
        struct = json.loads(response.content)
        ok_(isinstance(struct, list))
        eq_(len(struct), 0)

        User.objects.create(
          username=results[0][1]['uid'],
          email=results[0][1]['mail'].upper(),
          first_name=results[0][1]['givenName'],
          last_name=results[0][1]['sn'],
        )
        response = self.client.get(url, {'term': 'peter'})
        eq_(response.status_code, 200)
        struct = json.loads(response.content)
        eq_(len(struct), 1)

        first_item = struct[0]

        label = '%s %s <%s>' % (u'Pet\xe3r',
                                u'Bengtss\xa2n',
                                'peterbe@mozilla.com')
        value = label
        eq_(first_item, {
          'id': 'pbengtsson',
          'label': label,
          'value': value,
        })
