
from tests.api_tests import APITestBase
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
        assert self.api
        

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
        api, app = create_api(flask_conf={'DEBUG': True, 'ENVIRONMENT_NAME': 'local'})
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
