import os
from tests.api_tests import APITestBase
import logging
from hoops.logger import configure_logging
from hoops.status import library as status_library


class TestLogger(APITestBase):

    logger = None

    @classmethod
    def setup_app(cls):
        app = cls._app
        app.config['DEBUG'] = False
        # jetlaunch = Jetlaunch()
        here = os.path.abspath(os.path.dirname(__file__))
        log_configfile = os.path.join(here, 'test_logger.yaml')
        cls.log_file = os.path.join(here, 'hoops_test.log')
        # try:
        #     os.remove(cls.log_file)
        # except OSError:
        #     pass
        configure_logging(log_configfile, log_path=here, log_level='DEBUG', app_name='hoops')
        cls.logger = logging.getLogger('test')

        @app.route('/500', methods=['POST'])
        def unhandled_exception():
            raise status_library.API_UNHANDLED_EXCEPTION

    def delete_content_and_close(self, f):
        # f.seek(0)
        # f.truncate()
        f.close()
        pass

    def test_01_log_exception(self):
        rv = self.app.post(self.url_for('unhandled_exception'))

        f = open(self.log_file, 'r+')
        data = f.read()
        assert '500' in data, data
        assert 'ERROR' in data, data
        assert 'tests/api_tests/test_logger.py' in data, data
        assert 'An internal server error occurred' in data
        assert ' in unhandled_exception' in data, data
        assert 'raise status_library.API_UNHANDLED_EXCEPTION' in data, data
        self.delete_content_and_close(f)

    def test_02_different_log_levels(self):
        with self._app.test_request_context():
            self.logger.critical('Log level - critical')
            self.logger.warning('Log level - warning')
            self.logger.info('Log level - info')

            f = open(self.log_file, 'r+')
            data = f.read()

            assert 'Log level - critical' in data, data
            assert 'CRITICAL'in data, data

            assert 'Log level - warning' in data, data
            assert 'WARNING'in data, data

            assert 'Log level - info' in data, data
            assert 'INFO'in data, data
            self.delete_content_and_close(f)
