from sqlalchemy.exc import IntegrityError
from tests.api_tests import APITestBase
from tests.models_tests import ModelsTestBase
from test_models.basekit import BaseKitBrand, BaseKitSite
from test_models.core import User
from test_models.common import BaseModel
import time


class TestBaseKitUserModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        APITestBase.populate(self.db)

    def test_02_for_fk_reference_to_basekit_brand(self):
        ''' Check the FK reference of BaseKitSite to BaseKitBrand.'''
        my_bk_site = BaseKitSite.query.first()
        my_bk_brand = my_bk_site.brand  # via backref
        bk_sites_for_brand = BaseKitBrand.query.filter_by(
            id=my_bk_brand.id).first().basekit_sites  # via relationship
        assert my_bk_site in bk_sites_for_brand, "Test for checking the FK reference of BaseKitSite to BaseKitBrand failed"

    def test_03_for_fk_reference_to_user(self):
        ''' Check the FK reference of BaseKitSite to User. '''
        my_bk_site = BaseKitSite.query.first()
        my_bk_user = my_bk_site.user  # via backref
        bk_sites_for_user = User.query.filter_by(
            id=my_bk_user.id).first().basekit_sites  # via relationship
        assert my_bk_site in bk_sites_for_user, "Test for checking the FK reference of BaseKitSite to User failed"

    def test_04_for_repr(self):
        '''Test the __repr__ of BaseKitSite model.'''
        first_bk_site = BaseKitSite.query.first()
        assert "<BaseKitSite('" + str(first_bk_site.id) + "')>" in first_bk_site.__repr__(
        ), "Test for BaseKitSite __repr__ failed"

    def test_05_for_unique_bk_site_id(self):
        '''Test the uniqueness of bk_site_id.'''
        my_bk_site_id = BaseKitSite.query.first().bk_site_id
        bk_brand = BaseKitBrand.query.first()
        user = User.query.first()
        self.db.session.add(
            BaseKitSite(brand=bk_brand, user=user, bk_site_id=my_bk_site_id, basekit_package_id='2', subdomain="com"))
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, "Test for checking uniqueness of bk_site_id failed"

    def test_06_for_unique_basekit_package_id(self):
        '''Test the uniqueness of basekit_package_id.'''
        my_basekit_package_id = BaseKitSite.query.first().basekit_package_id
        brand = BaseKitBrand.query.first()
        user = User.query.first()
        self.db.session.add(
            BaseKitSite(brand=brand, user=user, bk_site_id='5', basekit_package_id=my_basekit_package_id, subdomain='in'))
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, "Test for checking uniqueness of basekit_package_id failed"

    def test_07_get_the_inherited_class(self):
        ''' Check the inherited BaseModel model class.'''
        baskekit_site = BaseKitSite()
        assert isinstance(
            baskekit_site, BaseModel), "Test to check inheritance of BaseKitSite from BaseModel failed"

    def test_08_for_bk_user_updation(self):
        ''' Check the BaseKitSite updation. '''
        first_bk_site = BaseKitSite.query.first()
        my_bk_site_created_at = first_bk_site.created_at
        my_bk_site_updated_at = first_bk_site.updated_at
        time.sleep(1)
        self.db.session.merge(
            BaseKitSite(id=first_bk_site.id, bk_site_id='8'))
        try:
            self.db.session.commit()
            assert my_bk_site_created_at == BaseKitSite.query.first().created_at, 'Test for checking whether "created_at" is not changing failed'
            assert my_bk_site_updated_at != BaseKitSite.query.first().updated_at, 'Test for checking whether "updated_at" changes failed'
            assert True
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitSite fields failed')

    def test_to_json(self):
        '''Check that serialization works'''
        site = BaseKitSite.query.first()
        out = site.to_json()
        for col in ['status', 'front_end_ip_addresses', 'user_id', 'service', 'created_at', 'updated_at', 'template_id', 'package_id', 'domains', 'id', 'front_end_cnames']:
            assert col in out, '%s not found in result of BaseKitSite.to_json()' % col
        assert out['service'] == 'builder'
        