
from apps.api.status import library as status
from apps.api.response import APIResponse
from tests.api_tests import APITestBase


class TestResponse(APITestBase):

    def test_basic(self):
        response = APIResponse('mine')
        assert response().keys() == ['response_data', 'status_code', 'status_message', 'api_version']
        assert response.response['response_data'] is 'mine'
        assert response()['response_data'] is 'mine'
        assert response.to_json() is response()
        assert response()["status_message"] == 'Ok'
        assert response()["status_code"] == 1000

    def test_extra(self):
        response = APIResponse({}, extra={"fanciful": "items"})
        assert 'fanciful' in response()

    def test_status(self):
        response = APIResponse('mine', status=status.API_FORBIDDEN)
        assert response()["status_message"] == 'The API request is not allowed.'
        assert response()["status_code"] == 4003
