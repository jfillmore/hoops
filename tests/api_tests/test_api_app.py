
from tests.api_tests import APITestBase
import json


class TestAPIApp(APITestBase):

    def test_app(self):
        from apps.api import flask, api, babel, assets
        assert flask
        assert api
        assert babel
        assert assets is not None

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
        from apps.api import create_app
        app = create_app(environment=None)
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
