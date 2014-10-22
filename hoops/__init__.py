__import__('pkg_resources').declare_namespace(__name__)

# from os import environ
import warnings
from flask import Flask
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from os.path import exists
import yaml

db = SQLAlchemy()

from hoops.restful import API, OAuthAPI
import hoops.json_add_to_json_hack
from hoops.utils import find_subclasses
from hoops.base import APIResource
from hoops.logger import configure_logging

SQLALCHEMY_DATABASE_URI = None
api = None

loglevel = {
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10,
    'NOTSET': 0,
}

__all__ = ['api', 'db', 'create_api', 'load_config']


def create_api(config_file='', app_name=None, rest_args=None, db_config=None, log_config=None, flask_conf=None, oauth_args=None):
    '''
    Creates a RESTFul API to which Resource-based views can be registered.

    ARGUMENTS:
       config_file: The application and logging configuration file
       app_name: The name of the API application
       rest_args: Arguments to pass on to Flask RESTful model (e.g. catch_all_404s, see http://flask-restful.readthedocs.org/en/latest/api.html#id1)
       flask_conf: Object from which addition flask arguments are parsed (see http://flask.pocoo.org/docs/config/)
       oauth_args: If given, the all Resources will require oauth authentication by default. The arguments given determine how the server's oauth
                   keys are selected based on oauth_provider.py (TODO: set arg signature!)
    '''

    global flask, api, db

    app_config, log_config, SQLALCHEMY_DATABASE_URI = load_config(config_file=config_file, environment_name=flask_conf['ENVIRONMENT_NAME'], db_config=db_config)

    flask_conf['ENVIRONMENT_NAME'] = flask_conf['ENVIRONMENT_NAME'] or 'local'

    if not app_name:
        app_name = 'Unnamed Application'
    if not rest_args:
        rest_args = {}

    flask = Flask(app_name)
    if flask_conf:
        flask.config.update(flask_conf)
    if isinstance(oauth_args, dict):
        rest_args['oauth_args'] = oauth_args
        api = OAuthAPI(flask, **rest_args)
    else:
        api = API(flask, **rest_args)

    babel = Babel(flask)

    if app_config.get('debug'):
        flask.config['DEBUG'] = True

    # not all RESTFul APIs will have a database associated with it
    # if isinstance(db_config, dict):
    #     SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@localhost/%(database)s?charset=utf8' % db_config

    if SQLALCHEMY_DATABASE_URI is not None:
        flask.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        db.init_app(flask)

    [api.register(sub) for sub in find_subclasses(APIResource)]

    # Enable logging if not disabled explicitly
    if not app_config.get('disable_logging'):
        # Set all log handlers to DEBUG if debug is enabled
        if flask.config.get('DEBUG'):
            log_level = 'DEBUG'
            for key, value in log_config.iteritems():
                if key in ['handlers', 'loggers']:
                    for ikey, ivalue in value.iteritems():   # ikey => inner key, ivalue => inner value
                        if loglevel[ivalue['level']] > loglevel['DEBUG']:
                            ivalue['level'] = 'DEBUG'

        # configure_logging(config_filename=flask.config.get('LOG_CONFIG'), log_level=flask.config.get('LOG_LEVEL'), log_path=flask.config.get('LOG_PATH'), app_name=app_name)
        configure_logging(logging_config=log_config, app_name=app_name, log_level=log_level)

    return flask, db


def load_config(config_file='', environment_name='local', database_url_only=False, db_config=None):
    global SQLALCHEMY_DATABASE_URI

    config = load_config_file(config_file, False)
    app_config = config.get('app').get(environment_name)
    log_config = config.get('logging')

    if type(app_config) is not dict:
        raise Exception("Application is not configured for %s environment!" % environment_name)

    if type(log_config) is not dict:
        warnings.warn('Logging configuration not found in %s ! Using hoops\' default logging configuration.' % config_file)

    if isinstance(db_config, dict):
        SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@localhost/%(database)s?charset=utf8' % db_config
    elif app_config.get('database'):
        SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@localhost/%(database)s?charset=utf8' % app_config.get('database')

    if database_url_only is True:
        return SQLALCHEMY_DATABASE_URI

    return app_config, log_config, SQLALCHEMY_DATABASE_URI


def load_config_file(config_file, environment):
    if not exists(config_file):
        raise Exception('Local configuration file {path} missing.'.format(path=config_file))

    with open(config_file) as f:
        cfg_string = f.read()

    config = yaml.load(cfg_string)

    if not config:
        raise Exception('Local configuration file {path} contains no config information!'.format(path=config_file))

    if environment:
        return config.get(environment)

    return config
