from configobj import ConfigObj
from os.path import expanduser, exists

configFile = expanduser('~') + '/.jetlaunch_config'
if not exists(configFile):
    raise Exception('Local configuration file {path} missing.'.format(path=configFile))

configuration_object = ConfigObj(configFile)

try:
    SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@localhost/%(database)s?charset=utf8' % configuration_object['DATABASE']['TEST']
    DEBUG = True
    ASSETS_DEBUG = True
except KeyError as ke:
    raise Exception('Missing section in configuration file. {error}'.format(error=ke.message))
