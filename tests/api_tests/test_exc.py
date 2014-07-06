

from tests.api_tests import APITestBase
from apps.api.exc import APIValidationException
from apps.api.status import library


class TestAPIExc(APITestBase):

    def test_api_exception(self):
        test = library.API_UNHANDLED_EXCEPTION
        assert isinstance(test, Exception)
        assert test.http_status
        assert test.status_code

        assert 'status_code' in test.get_dict()
        assert 'status_message' in test.get_dict()

    def test_api_validation_exception(self):
        failure = APIValidationException(status=library.API_INPUT_VALIDATION_FAILED, validation_errors={"test": "It broke"})
        assert 'validation_errors' in failure.extra
