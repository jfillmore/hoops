
from tests.api_tests import APITestBase
from apps.api.status import MissingParameterError, APIStatus, library
import unittest


class TestAPIApp(APITestBase, unittest.TestCase):

    def test_bare_apistatus(self):
        status = APIStatus(200, 1000, "OK")
        assert status.__repr__()  # make sure it works
        assert status.message == "OK"
        assert status.status_code == 1000
        assert status.http_status == 200

    def test_get_dict(self):
        status = APIStatus(200, 1000, "OK")
        assert status.get_dict() == {
            "status_code": 1000,
            "status_message": "OK",
        }

    def test_attempt_params_with_no_args(self):
        with self.assertRaises(MissingParameterError):
            APIStatus(200, 1000, "OK - %(test)s")

    def test_attempt_params_with_args(self):
        status = APIStatus(200, 1000, "OK - %(test)s", test="tested")
        assert status.message == "OK - tested"

    def test_library_accessor(self):
        status = library.API_OK
        assert status.message == "Ok", status.message

    def test_library_accessor_not_found_raises(self):
        with self.assertRaises(KeyError):
            library.NOTFOUND

    def test_library_kwargs(self):
        status = library.get('API_FORBIDDEN_ACCESS', child_resource='test', parent_resource='test')
        assert '%' not in status.message

    def test_unmodifiable(self):
        status = library.get('API_FORBIDDEN_ACCESS', child_resource='test', parent_resource='test')
        with self.assertRaises(AttributeError):
            status.message = 'test'
