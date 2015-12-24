#!/usr/bin/env python

import sys
import os

import argparse
from configure import Configuration

from hoops.core import create_api
from hoops.utils import find_subclasses


DEFAULT_CONF = 'hoops-api.yml'
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8000  # starting port number


class HoopsSubParser(object):
    branch = None   # must be set for sub-branches!
    help = 'Sub-parser description'

    def __init__(self, subparser):
        if self.branch is None:
            raise Exception("Invalid Hoops sub-parser; no branch is set.")
        return subparser

    def invoke(self, options, flask_app, db):
        # perform sub-parser specifiec handling of the options
        print "Invoked with options %s" % options


class HoopsDbSubParser(HoopsSubParser):
    branch = 'db'
    help = 'Database manipulation'
    db_actions = ['manage', 'recreate']  # TODO: populate

    def __init__(self, subparser):
        super(HoopsDbSubParser, self).__init__(subparser)
        subparser.add_argument(
            'db_action',
            help='Database action to perform',
            choices=self.db_actions
        )

    def invoke(self, options, flask_app, db):
        if options.db_action == 'manage':
            from flask.ext.script import Manager
            from flask.ext.alembic import ManageMigrations
            manager = Manager(flask_app)
            manager.add_command("migrate", ManageMigrations())
        elif options.db_action == 'recreate':
            from hoops.dbmanager import DBManager
            with flask_app.app_context():
                DBManager(db).recreate_db()


class HoopsRunSubParser(HoopsSubParser):
    branch = 'run'
    help = 'Database manipulation'

    def __init__(self, subparser):
        super(HoopsRunSubParser, self).__init__(subparser)
        subparser.add_argument(
            "--app", required=True,
            help="Application to run API configuration file"
        )
        subparser.add_argument(
            "--host", default=DEFAULT_HOST,
            help="Hostname to run development mode server on"
        )
        subparser.add_argument(
            "--port", default=DEFAULT_PORT,
            help="Port to run development mode server on"
        )

    def invoke(self, options, flask_app, db):
        # TODO: use app_args for host/port/etc if not given by options
        flask_app.run(host=options.host, port=int(options.port))


class HoopsApi(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument(
            "--config", default=DEFAULT_CONF,
            help="Hoops API configuration file"
        )
        self.parser = parser
        self.flask_app = None
        self.db = None
        self.hoops_api = None
        self.options = None  # selected options
        self.sub_parsers = {}  # ArgParse subparsers
        self._init_sub_parsers()

    def _init_sub_parsers(self):
        hoops_sub_parsers = find_subclasses(HoopsSubParser)
        if hoops_sub_parsers:
            sub_parsers = self.parser.add_subparsers(
                title='API command',
                help='API management actions',
                dest='branch'
            )
            for hoops_sub_parser in hoops_sub_parsers:
                # register the sub-parser, allowing it to add extra args
                sub_parser = sub_parsers.add_parser(
                    hoops_sub_parser.branch,
                    help=hoops_sub_parser
                )
                self.sub_parsers[hoops_sub_parser.branch] = hoops_sub_parser(sub_parser)

    def parse_options(self, args=None):
        if args is None:
            options = self.parser.parse_args()
        else:
            options = self.parser.parse_args(args)
        self.options = options
        self._init_app()
        return options

    def process_options(self):
        # determine which sub-parser was invoked
        self.sub_parsers[self.options.branch].invoke(
            self.options,
            self.flask_app,
            self.db
        )

    def _init_app(self, app_slug=None, options=None):
        # regardless of the action, we need an app created
        if options is None:
            options = self.options
        config = Configuration.from_file(options.config)
        # add directory config file is in to include path for models/views
        sys.path.append(os.path.dirname(options.config))
        if 'app_args' not in config:
            config.app_args = {}
        if 'apps' not in config or not config.apps:
            raise Exception("No applications defined in configuration file %s" % options.config)
        self.config = config
        if app_slug is None:
            app_slug = config.apps.keys()[0]
        app_conf = config.apps[app_slug]
        # build args based on app
        flask_args = config.app_args.get('flask', {})
        flask_args.update(app_conf.get('args', {}).get('flask', {}))
        flask_config = {
            'DEBUG': bool(config.app_args.get('debug', False))
        }
        if 'flask' in app_conf.get('args', {}):
            flask_config.update(app_conf.args.flask)
        if 'debug' in app_conf.get('args', {}):
            flask_config['DEBUG'] = app_conf.args.debug
        # configure the database connection, if needed
        db_config = None
        db_obj = None
        if 'db' in config:
            db_config = {
                'username': config.db.get('user', 'root'),
                'password': config.db.get('pass', ''),
                'hostname': config.db.get('host', 'localhost'),
                'database': config.db.get('name', app_slug)
            }
            if 'models' in config.db:
                db_module = config.db.models.get('module')
                db_include = config.db.models.get('include')
                if db_module and db_include:
                    # importing the DB module should also capture all the database objects referenced by it
                    (db_import) = __import__(
                        db_module,
                        globals(),
                        locals(),
                        [db_include],
                        -1
                    )
                    db_obj = getattr(db_import, db_include)
        # finally, import application views
        if 'views' in app_conf:
            views_module = app_conf.views.get('module')
            views_include = app_conf.views.get('include')
            if views_module and views_include:
                # importing the views module should also capture all the database objects referenced by it
                # the object itself we don't care about however
                (views_obj) = __import__(
                    views_module,
                    globals(),
                    locals(),
                    [views_include],
                    -1
                )
        self.flask_app, self.db, self.hoops_api = create_api(
            app_name=app_conf.get('name', app_slug),
            database=db_obj,
            db_config=db_config,
            flask_config=flask_config
        )
        return {
            'flask_app': self.flask_app,
            'db': self.db,
            'hoops_api': self.hoops_api
        }


def main():
    hoops_api = HoopsApi()
    hoops_api.parse_options()
    hoops_api.process_options()

if __name__ == '__main__':
    main()
