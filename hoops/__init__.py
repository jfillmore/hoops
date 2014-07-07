__import__('pkg_resources').declare_namespace(__name__)

from os import environ

from flask import Flask

from hoops.restful import API
import hoops.json_add_to_json_hack


flask = None
api = None
db = None

VERSION = "1.0.0"


def create_app(database, app_name=None, rest_args=None, flask_conf=None):
    global flask, api

    if not app_name:
        app_name = __name__
    if not rest_args:
        rest_args = {}

    db = database
    flask = Flask(app_name)
    if flask_conf:
        flask.config.from_object(flask_conf)
    api = API(flask, **rest_args)
    db.init_app(flask)
    return api, flask
