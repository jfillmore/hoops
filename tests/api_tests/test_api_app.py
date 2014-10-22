
from tests.api_tests import APITestBase, config_file, db_config
import simplejson as json

from hoops import create_api
from hoops.base import APIResource
from hoops.response import APIResponse


class HelloWorld(APIResource):
    route = '/'

    def get(self):
        return APIResponse(["hello", "it works"])


class TestAPIApp(APITestBase):

    def test_app(self):
        assert self._app

    def test_get(self):
        rv = self.app.get("/")
        assert rv.status_code == 200
        out = json.loads(rv.data)
        assert 'api_version' in out
        assert 'response_data' in out
        assert 'status_code' in out
        assert 'status_message' in out
        assert 'hello' in out['response_data']

    def test_create_app_with_no_environment(self):
        (app, db) = create_api(db_config=db_config, config_file=config_file, flask_conf={'DEBUG': True, 'ENVIRONMENT_NAME': 'local'}, app_name='hoops',)
        assert app.config.get('ENVIRONMENT_NAME') == 'local'

    def test_create_app_with_no_app_name(self):
        (app, db) = create_api(db_config=db_config, config_file=config_file, flask_conf={'DEBUG': True, 'ENVIRONMENT_NAME': 'local'}, app_name='hoops',)
        assert app.config.get('ENVIRONMENT_NAME') == 'local'

    def test_404(self):
        rv = self.app.get("/missing")
        assert rv.status_code == 404
        out = json.loads(rv.data)
        assert 'api_version' in out
        assert 'response_data' in out
        assert 'status_code' in out
        assert 'status_message' in out
        assert out['response_data'] is None
