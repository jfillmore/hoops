from models.basekit import BaseKitCluster, BaseKitBrand, BaseKitPackage
from tests.models_tests import ModelsTestBase
from tests.api_tests import APITestBase
from sqlalchemy.exc import IntegrityError
import time


class TestBaseKitBrandModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        APITestBase.populate(self.db)

    def test_02_for_fk_reference_to_basekit_cluster(self):
        ''' Check the FK reference of BaseKitPackage to BaseKitCluster. '''
        my_bk_package = BaseKitPackage.query.first()
        my_bk_cluster = my_bk_package.cluster  # via backref
        bk_packages_for_cluster = BaseKitCluster.query.filter_by(
            id=my_bk_cluster.id).first().basekit_packages  # via relationship
        assert my_bk_package in bk_packages_for_cluster, "Test for checking the FK reference of BaseKitPackage to BaseKitCluster failed"

    def test_03_for_fk_reference_to_basekit_brand(self):
        ''' Check the FK reference of BaseKitPackage to BaseKitBrand.'''
        my_bk_package = BaseKitPackage.query.first()
        my_bk_brand = my_bk_package.brand  # via backref
        bk_brands_for_package = BaseKitBrand.query.filter_by(
            id=my_bk_brand.id).first().basekit_packages  # via relationship
        assert my_bk_package in bk_brands_for_package, "Test for checking the FK reference of BaseKitPackage to BaseKitBrand failed"

    def test_04_for_default_provisioning(self):
        '''Test the default enabled.(True)'''
        cluster = BaseKitCluster.query.first()
        brand = BaseKitBrand.query.first()
        self.db.session.add(
            BaseKitPackage(name="Test BK Package 4", description='test package desc4', cluster_id=cluster.id, brand_id=brand.id, bk_package_id='4'))
        self.db.session.commit()
        bk_package_enbled = BaseKitPackage.query.filter_by(
            bk_package_id='4').first().enabled
        assert bk_package_enbled, "Test for checking default enabled failed"

    def test_05_get_the_inherited_class(self):
        ''' Check the inherited BaseModel model class.'''
        from models.common import BaseModel
        baskekit_package = BaseKitPackage()
        assert isinstance(
            baskekit_package, BaseModel), "Test to check inheritance of BaseKitPackage from BaseModel failed"

    def test_06_for_bkpackage_updation(self):
        ''' Check the BaseKitPackage updation. '''
        first_bk_package = BaseKitPackage.query.first()
        my_bk_package_created_at = first_bk_package.created_at
        my_bk_package_updated_at = first_bk_package.updated_at
        time.sleep(1)
        self.db.session.merge(
            BaseKitPackage(id=first_bk_package.id, name='Changed Package', description='updated description 1'))
        try:
            self.db.session.commit()
            assert my_bk_package_created_at == BaseKitPackage.query.first().created_at, \
                'Test for checking whether "created_at" is not changing failed'
            assert my_bk_package_updated_at != BaseKitPackage.query.first().updated_at, 'Test for checking whether "updated_at" changes failed'
            assert True
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitPackage fields failed')

    def test_08_for_repr(self):
        '''Test the __repr__ of BaseKitPackage model.'''
        first_bk_package = BaseKitPackage.query.first()
        assert "<BaseKitPackage('" + str(first_bk_package.id) + "', '" + \
            first_bk_package.name + \
            "')>" in first_bk_package.__repr__(
            ), "Test for BaseKitPackage __repr__ failed"

    def test_09_for_unique_bk_package_id(self):
        '''Test the uniqueness of bk_package_id.'''
        cluster = BaseKitCluster.query.first()
        brand = BaseKitBrand.query.first()
        my_bk_package_id = BaseKitPackage.query.first().bk_package_id
        self.db.session.add(
            BaseKitPackage(name="Test BK Package 5", description='test package desc5', cluster_id=cluster.id, brand_id=brand.id,
                           bk_package_id=my_bk_package_id))
        try:
            self.db.session.commit()
        except Exception:
            assert IntegrityError, "Test for checking uniqueness of bk_package_id failed"
