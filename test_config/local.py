
from configobj import ConfigObj
from os.path import expanduser, exists

configFile = expanduser('~') + '/.jetlaunch_config'
if not exists(configFile):
	raise Exception('Local configuration file {path} missing.'.format(path=configFile))

configuration_object = ConfigObj(configFile)
#Going to read the local configuration file at ~/.jetlaunch_config
try:
	SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@localhost/%(database)s?charset=utf8' % configuration_object['DATABASE']['LOCAL']
	DEBUG = True
	ASSETS_DEBUG = True
except KeyError as ke:
	raise Exception('Missing section in configuration file. {error}'.format(error=ke.message))

LOG_FILE = None

# Postmark dev config
MAIL_SERVER = 'smtp.postmarkapp.com'
MAIL_PORT = 2525
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'b4637dd8-f29b-4b0c-a6e4-e24835851171'
MAIL_PASSWORD = 'b4637dd8-f29b-4b0c-a6e4-e24835851171'
MAIL_DEFAULT_SENDER = 'hello@jetlaunch.co'

ENVIRONMENT_NAME = 'local'  # Used for test suite
ERROR_404_HELP = False
