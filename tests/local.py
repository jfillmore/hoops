from config.test import configuration_object

try:
    SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@localhost/%(database)s?charset=utf8' % configuration_object['DATABASE']['TEST']
    DEBUG = True
    ASSETS_DEBUG = True
except KeyError as ke:
    raise Exception('Missing section in configuration file. {error}'.format(error=ke.message))
