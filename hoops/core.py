# from os import environ
from flask import Flask
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from os.path import exists
import warnings
import yaml

from hoops.base import APIResource
from hoops.logger import configure_logging
from hoops.utils import find_subclasses
import hoops.json_add_to_json_hack

SQLALCHEMY_DATABASE_URI = None
api = None
db = None


def create_api(app_name, rest_args=None, database=None, db_config=None, log_config=None, flask_config=None, oauth_args=None):
    '''
    Creates a RESTFul API to which Resource-based views can be registered.

    ARGUMENTS:
       app_name: The name of the API application
       rest_args: Arguments to pass on to Flask RESTful model (e.g. catch_all_404s, see http://flask-restful.readthedocs.org/en/latest/api.html#id1)
       database: SQLAlchemy object to initialize with the application
       db_config: Dictionary of username/password/hostname/database_name
       log_config: Overrides default logging configuration
       flask_config: Object from which addition flask arguments are parsed (see http://flask.pocoo.org/docs/config/)
       oauth_args: If given, the all Resources will require oauth authentication by default. The arguments given determine how the server's oauth
                   keys are selected based on oauth_provider.py (TODO: set arg signature!)
    '''

    global flask, api, db, SQLALCHEMY_DATABASE_URI

    if flask_config is None:
        flask_config = {}
    flask_config['ENVIRONMENT_NAME'] = flask_config.get('ENVIRONMENT_NAME',  'local')

    if not rest_args:
        rest_args = {}

    flask = Flask(app_name)
    if flask_config:
        flask.config.update(flask_config)
    # only import the API class needed, to avoid oauth deps
    if isinstance(oauth_args, dict):
        rest_args['oauth_args'] = oauth_args
        from hoops.restful import OAuthAPI
        api = OAuthAPI(flask, **rest_args)
    else:
        from hoops.restful import API
        api = API(flask, **rest_args)
    babel = Babel(flask)
    # prep the database if needed; not all RESTFul APIs will have a database associated with it
    if database is not None and isinstance(db_config, dict):
        db = database
        SQLALCHEMY_DATABASE_URI = 'mysql://%(username)s:%(password)s@%(hostname)s/%(database)s?charset=utf8' % db_config
        flask.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        db.init_app(flask)
        flask.db = db
    # setup logging
    if flask.config.get('DEBUG'):
        log_level = 'DEBUG'
    else:
        log_level = 'WARNING'
    configure_logging(app_name, logging_config=log_config, log_level=log_level)
    # locate and register all of the views we can find
    [api.register(sub) for sub in find_subclasses(APIResource)]
    return flask, db, api


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
