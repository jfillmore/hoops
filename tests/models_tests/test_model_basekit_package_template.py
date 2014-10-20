
from tests.models_tests import ModelsTestBase
from tests.api_tests import APITestBase
from test_models.basekit import BaseKitPackageTemplate, BaseKitProvisioningHelper, BaseKitPackage, BaseKitCluster, BaseKitSite
from test_models.core import Package, Partner, User, Customer
from hoops.utils import BaseModel
import time


class TestBaseKitPackageTemplateModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        APITestBase.populate(self.db)

    def test_02_for_repr(self):
        '''Test the __repr__ of BaseKitPackageTemplate model.'''
        first_bk_package_templ = BaseKitPackageTemplate.query.first()
        assert "<BaseKitPackageTemplate('" + str(first_bk_package_templ.id) + "')>" in first_bk_package_templ.__repr__(
        ), "Test for BaseKitPackageTemplate __repr__ failed"

    def test_04_get_the_inherited_class(self):
        ''' Check the inherited BaseModel model class. '''
        baskekit_package_templ = BaseKitPackageTemplate()
        assert isinstance(
            baskekit_package_templ, BaseModel), "Test to check inheritance from BaseModel failed"

    def test_05_for_bk_node_updation(self):
        ''' Check the BaseKitPackageTemplate updation. '''
        first_bk_package_template = BaseKitPackageTemplate.query.first()
        my_package_template_created_at = first_bk_package_template.created_at
        my_package_template_updated_at = first_bk_package_template.updated_at
        time.sleep(1)
        self.db.session.merge(
            BaseKitPackageTemplate(id=first_bk_package_template.id, name='Updated BK Package Template'))
        try:
            self.db.session.commit()
            assert my_package_template_created_at == BaseKitPackageTemplate.query.first().created_at, \
                'Test for checking whether "created_at" is not changing failed'
            assert my_package_template_updated_at != BaseKitPackageTemplate.query.first().updated_at, \
                'Test for checking whether "updated_at" changes failed'
            assert True
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitPackageTemplate fields failed')

    def test_06_for_basekit_pakcage_template_fk_reference(self):
        '''Check the validity of FK reference to package_id'''
        my_bk_package_template = BaseKitPackageTemplate.query.first()
        my_bk_package = my_bk_package_template.package
        bk_package_templates = Package.query.filter_by(id=my_bk_package.id).first().basekit_templates
        assert my_bk_package_template in bk_package_templates, 'Test for checking the validity of FK reference to package_id failed'

    def test_07_for_basekit_provisioning_helper(self):
        ''' Test to impart coverage to basekit.BaseKitProvisioningHelper'''
        p = Partner.query.filter_by(name='enom').one()
        brand = BaseKitProvisioningHelper.map_partner_to_brand(p)
        bkp = BaseKitPackage.query.first()
        cluster = BaseKitCluster.query.first()
        BaseKitProvisioningHelper.find_basekit_package(brand, Customer.query.first())
        self.db.session.add(BaseKitSite(brand=brand, user=User.query.first(), bk_site_id='fake1', basekit_package=bkp,
                            subdomain='test.bkreseller.com', basekit_node_id=cluster.basekit_nodes[0].id))
        self.db.session.commit()
        BaseKitProvisioningHelper.find_unused_subdomain(brand, 'faketest')
        BaseKitProvisioningHelper.find_unused_subdomain(brand, 'bkreseller.com')
        assert True

    def test_to_json(self):
        '''Check that BaseKitPackageTemplate serialization works'''
        pktpl = BaseKitPackageTemplate.query.first()
        out = pktpl.to_json()
        assert type(out) == dict
        assert 'tag' in out
        assert 'id' in out
        assert 'name' in out
