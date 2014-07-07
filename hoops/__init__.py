from os import environ

from flask import Flask

from hoops.restful import API, OAuthAPI
import hoops.json_add_to_json_hack


flask = None
api = None
database = None

VERSION = "1.0.0"


def create_api(database=None, app_name=None, rest_args=None, flask_conf=None, oauth_args=None):
    '''
    Creates a RESTFul API to which Resource-based views can be registered.

    ARGUMENTS:
       database: The database object, if needed, to to use for model-based API resources
       app_name: The name of the API application
       rest_args: Arguments to pass on to Flask RESTful model (e.g. catch_all_404s, see http://flask-restful.readthedocs.org/en/latest/api.html#id1)
       flask_conf: Object from which addition flask arguments are parsed (see http://flask.pocoo.org/docs/config/)
       oauth_args: If given, the all Resources will require oauth authentication by default. The arguments given determine how the server's oauth keys are selected based on oauth_provider.py (TODO: set arg signature!)
    '''

    global flask, api

    if not app_name:
        app_name = 'Unnamed Application'
    if not rest_args:
        rest_args = {}

    flask = Flask(app_name)
    if flask_conf:
        flask.config.from_object(flask_conf)
    if isinstance(oauth_args, object):
        api = OAuthAPI(flask, **rest_args)
    else:
        api = API(flask, **rest_args)
    # not all RESTFul APIs will have a database associated with it
    if database:
        database.init_app(flask)
    return api, flask
