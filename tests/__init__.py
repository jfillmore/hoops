
from flask import url_for
from hoops.utils import TestUtilities
from hoops import load_config_file

from os.path import expanduser

config_file = expanduser('~') + '/.hoops.yml'
db_config_file = expanduser('~') + '/.hoops_db.yml'

db_config = load_config_file(db_config_file, 'test')


class TestBase(object):

    @classmethod
    def setup_class(cls):
        cls._app = cls.get_app()
        # cls._app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%(username)s:%(password)s@localhost/%(database)s?charset=utf8' % db_config
        cls._app.config['TESTING'] = True
        if cls.db and not cls.db.app:
            cls.db.init_app(cls._app)
            cls.db.app = cls._app
        if cls.db:
            cls.db.create_all()
            TestUtilities.clear_database(cls.db)
        cls.app = cls._app.test_client()

        #from jetlaunch.consumer import BaseKitAPIClient as BK
        #BK.enable_mock_api()

        cls.setup_app()

    @classmethod
    def setup_app(cls):
        pass

    @classmethod
    def teardown_class(cls):
        if cls.db:
            cls.db.session.remove()

    def url_for(self, endpoint, **kwargs):
        ctx = self._app.test_request_context()
        ctx.push()
        url = url_for(endpoint, **kwargs)
        ctx.pop()
        return url

    @classmethod
    def get_app(cls):

        from flask import Flask
        from os import environ

        app = Flask(__name__)

        if ('environment' in environ.keys()):
            config_object = 'config.' + environ['environment']
        else:
            config_object = 'config.local'

        app.config.from_object(config_object)

        return app

    def run_app(self):
        self.setup_class()
        self._app.run()
