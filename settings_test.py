# definitely don't want to slow down tests with bcrypt
PWD_ALGORITHM = 'sha521'

# never use a semi-persistent cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

AUTH_LDAP_BIND_PASSWORD = 'anything'
