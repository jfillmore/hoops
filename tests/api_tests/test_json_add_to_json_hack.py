
from tests.api_tests import APITestBase
import json


class TestAPIApp(APITestBase):

    def test_it(self):

        class WithToJson(object):
            def to_json(self):
                return {'test': 1}

        # This will fail if the monkeypatch in json_add_to_json_hack is not loaded
        json.dumps(WithToJson())
        assert True

