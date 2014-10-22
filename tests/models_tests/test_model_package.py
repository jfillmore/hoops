from tests.models_tests import ModelsTestBase
from test_models.core import Partner, Language, Package, Customer, PackageService, Service
from hoops.utils import OutputFormat
from tests import dbhelper
from test_models import db


class TestPackageModel(ModelsTestBase):

        def test_01_populate(self):
            ''' Populate the required Tables. '''
            self.populate_helper(lang=True, partner='test', customers=['test'], users=[])
            lang_en = Language.query.filter_by(lang='en').one()

            p1 = Partner.query.first()
            p2 = Partner(name='eNom_2', language=lang_en, output_format=OutputFormat.JSON, slug=None)
            p3 = Partner(name='eNom_3', language=lang_en, output_format=OutputFormat.JSON, slug=None)
            self.db.session.add_all([p2, p3])

            self.db.session.flush()

            c1 = Customer(name="TestCustomer1", my_identifier="test_customer_300", partner=p1, status='active')
            self.db.session.add_all([
                c1,
                Customer(name="TestCustomer2", my_identifier="test_customer_200", partner=p2, status='active'),
                Customer(name="TestCustomer3", my_identifier="test_customer_100", partner=p1, status='suspended'),
                Customer(name="TestCustomer4", my_identifier="test_customer_400", partner=p1, status='active')
            ])
            dbhelper.add(Package(name="Test Package 001", enabled=1, partner=p1, description='test_package 0001'), db)
            dbhelper.add(Package(name="Test Package 002", enabled=1, partner=p1, description='test_package 002'), db)
            dbhelper.add(Package(name="Test Package 003", enabled=0, partner=p1, description='test_package 003'), db)
            dbhelper.add(Package(name="Test Package 001", enabled=1, partner=p2, description='test_package 001 for partner 2'), db)

            assert Package.query.count() > 1

        def test_to_json(self):
            pkg = Package.query.first()
            svc = dbhelper.add(Service(name='Test Service', provisioning_enabled=True, slug=None), db)
            dbhelper.add(PackageService(package=pkg, service=svc), db)
            out = pkg.to_json()
            assert sorted(out.keys()) == ['created_at', 'description', 'enabled', 'id', 'name', 'services', 'updated_at'], sorted(out.keys())
            assert out['services'][0]['service'] == 'test-service'
