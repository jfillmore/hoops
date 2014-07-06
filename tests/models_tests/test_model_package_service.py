from tests.models_tests import ModelsTestBase
from config import OutputFormat
from models.core import PackageService, Package, Language, Partner, Service, PackageServiceParam


class TestPackageServiceModel(ModelsTestBase):

    def test_01_populate(self):
        l1 = Language(name="English", lang='en-US', active=1)

        p1 = Partner(name="TestPartner2", language=l1, output_format=OutputFormat.JSON, enabled=True)

        serv = Service(name='Test Service', provisioning_enabled=True, slug=None)

        pkg = Package(name="Test Package 001", enabled=1, partner=p1, description='test_package 0001')

        pkg_serv = PackageService(package=pkg, service=serv)

        pkg_serv_param_1 = PackageServiceParam(package_service=pkg_serv, param_name="test_param_name_1", param_value="test_param_val")
        pkg_serv_param_2 = PackageServiceParam(package_service=pkg_serv, param_name="test_param_name_2")
        pkg_serv_param_3 = PackageServiceParam(package_service=pkg_serv, param_name="test_param_name_3", param_value=123)
        pkg_serv_param_4 = PackageServiceParam(package_service=pkg_serv, param_name="test_param_name_4", param_value=123.123)

        self.db.session.add_all([pkg_serv, pkg_serv_param_1, pkg_serv_param_2, pkg_serv_param_3, pkg_serv_param_4])
        self.db.session.commit()
        assert PackageService.query.count() == 1
        assert PackageServiceParam.query.count() == 4

    def test_02_test_api_response(self):
        ps_inst_list = [x.to_json() for x in PackageService.query.all()]
        assert ps_inst_list[0]['test_param_name_1'] == "test_param_val"
        assert ps_inst_list[0]['test_param_name_2'] is None
        assert ps_inst_list[0]['test_param_name_3'] == 123
