from configobj import ConfigObj
from os.path import exists

configFile = '/etc/jetlaunch.conf'
if not exists(configFile):
    raise Exception('Jetlaunch configuration file {path} missing.'.format(path=configFile))

configuration_object = ConfigObj(configFile)

try:
    SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@%(hostname)s/%(database)s?charset=utf8' % configuration_object['DATABASE']['STAGE']
    DEBUG = True
    ASSETS_DEBUG = False



except KeyError as ke:
    raise Exception('Missing section in configuration file. {error}'.format(error=ke.message))

# Postmark stage config
MAIL_SERVER = 'smtp.postmarkapp.com'
MAIL_PORT = 2525
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = '978e0279-b530-441b-a753-3e35fd375e10'
MAIL_PASSWORD = '978e0279-b530-441b-a753-3e35fd375e10'
MAIL_DEFAULT_SENDER = 'hello@jetlaunch.co'
ERROR_404_HELP = False
