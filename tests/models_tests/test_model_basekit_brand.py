
from sqlalchemy.exc import IntegrityError
from models.basekit import BaseKitCluster, BaseKitBrand
from models.core import Partner
from tests.models_tests import ModelsTestBase
from tests.api_tests import APITestBase
from tests import dbhelper
import time


class TestBaseKitBrandModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        APITestBase.populate(self.db)

    def test_02_uniquenes_of_slug(self):
        '''Test for uniqueness of slug.'''
        first_bk_brand_slug = BaseKitBrand.query.first().slug
        self.db.session.add(
            BaseKitBrand(name="Test BK Brand Dup Slug", slug=str(first_bk_brand_slug), cluster_id=1, partner_id=1, bk_brand_id='10',
                         default_domain='http://www.yahoo.com'))
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, 'Test for checking uniqueness of slug failed'

    def test_03_for_repr(self):
        '''Test the __repr__ of BaseKitBrand model.'''
        first_bk_brand = BaseKitBrand.query.first()
        assert "<BaseKitBrand('" + str(first_bk_brand.id) + "', '" + \
            first_bk_brand.slug + \
            "')>" in first_bk_brand.__repr__(
            ), "Test for BaseKitBrand __repr__ failed"

    def test_04_entry_of_custom_slug(self):
        '''Test the entry of custom slug.'''
        cluster = BaseKitCluster.query.first()
        partner = Partner.query.first()
        self.db.session.add(
            BaseKitBrand(name="BaseKit Brand Testing Slug", slug='my_custom_slug_648', cluster=cluster, partner=partner, bk_brand_id='5',
                         default_domain='http://www.yahoo.com'))
        self.db.session.commit()
        custom_slug_bk_brand = BaseKitBrand.query.filter_by(
            slug='my_custom_slug_648').first()
        assert custom_slug_bk_brand, 'Test for checking entry of custom slug failed'

    def test_05_for_default_provisioning(self):
        '''Test the default provisioning_enabled.(True)'''
        cluster = BaseKitCluster.query.first()
        partner = Partner.query.first()
        self.db.session.add(
            BaseKitBrand(name="BaseKit Brand 124", cluster=cluster, partner=partner, bk_brand_id='6', default_domain='http://www.yahoo.com'))
        self.db.session.commit()
        bk_brand_provisioning = BaseKitBrand.query.filter_by(
            slug='basekit-brand-124').first().provisioning_enabled
        assert bk_brand_provisioning, "Test for checking default provisioning enabled failed"

    def test_06_get_the_inherited_class(self):
        ''' Check the inherited SluggableModel model class. '''
        from models.common import SluggableModel
        baskekit_brand = BaseKitBrand()
        assert isinstance(baskekit_brand, SluggableModel), "Test to check inheritance from SluggableModel failed"

    def test_07_for_bkbrand_updation(self):
        ''' Check the BaseKitBrand updation. '''
        first_bk_brand = BaseKitBrand.query.first()
        my_bk_brand_created_at = first_bk_brand.created_at
        my_bk_brand_updated_at = first_bk_brand.updated_at
        time.sleep(1)
        self.db.session.merge(
            BaseKitBrand(id=first_bk_brand.id, name='Changed Brand102', default_domain='http://www.bing.com'))
        try:
            self.db.session.commit()
            assert True
            assert my_bk_brand_created_at == BaseKitBrand.query.first().created_at, 'Test for checking whether "created_at" is not changing failed'
            assert my_bk_brand_updated_at != BaseKitBrand.query.first().updated_at, 'Test for checking whether "updated_at" changes failed'
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitBrand fields failed')

    def test_09_for_fk_reference_to_basekit_cluster(self):
        ''' Check the FK reference of BaseKitBrand to BaseKitCluster. '''
        my_bk_brand = BaseKitBrand.query.first()
        my_bk_brand_cluster = my_bk_brand.cluster  # via backref
        bk_brands_for_cluster = BaseKitCluster.query.filter_by(id=my_bk_brand_cluster.id).first().basekit_brands  # via relationship
        assert my_bk_brand in bk_brands_for_cluster, "Test for checking the FK reference of BaseKitBrand to BaseKitCluster failed"

    def test_10_for_fk_reference_to_partner(self):
        ''' Check the FK reference of BaseKitBrand to Partner. '''
        my_bk_brand = BaseKitBrand.query.first()
        my_bk_brand_partner = my_bk_brand.partner  # via backref
        bk_brands_for_partner = Partner.query.filter_by(id=my_bk_brand_partner.id).first().basekit_brands  # via relationship
        assert my_bk_brand in bk_brands_for_partner, "Test for checking the FK reference of BaseKitBrand to Partner failed"

    def test_11_for_uniqueness_of_bk_brand_id(self):
        ''' Check the uniqueness of bk_brand_id. '''
        cluster = BaseKitCluster.query.first()
        partner = Partner.query.first()
        my_bk_brand_id = BaseKitBrand.query.first().bk_brand_id
        self.db.session.add(
            BaseKitBrand(name="Test BK Brand Dup bk_brand_id", cluster=cluster, partner=partner, bk_brand_id=str(my_bk_brand_id),
                         default_domain='http://www.yahoo.com'))
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, 'Test for checking uniqueness of bk_brand_id failed'

    def test_12_basekit_oauth_fields(self):
        '''Test the oauth fields work'''
        brand = BaseKitBrand.query.first()
        brand.oauth_consumer_key = 'test'
        brand.oauth_consumer_secret = 'test test test'
        brand.oauth_token = 'test test test'
        brand.oauth_token_secret = 'test test test'
        dbhelper.update(brand, self.db)
