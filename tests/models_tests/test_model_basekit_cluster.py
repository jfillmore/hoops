from tests.models_tests import ModelsTestBase
from hoops.common import SluggableModel
from test_models.basekit import BaseKitCluster
from sqlalchemy.exc import IntegrityError
import time


class TestBaseKitClusterModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the basekit_cluster Table. '''
        self.db.session.add(
            BaseKitCluster(name="Test BK Cluster 1", description='BaseKit cluster testing', api_url='http://www.admin_global.com',
                           provisioning_enabled=True))
        self.db.session.add(
            BaseKitCluster(name="Test BK Cluster 2", slug='custom_slug_cluster_2', description='Another BaseKit cluster testing',
                           api_url='http://www.admin_america.com'))
        self.db.session.add(
            BaseKitCluster(name="Test BK Cluster 3", description='Last basekit cluster', api_url='http://www.admin_australia.com',
                           provisioning_enabled=False))
        self.db.session.commit()
        assert BaseKitCluster.query.count() == 3

    def test_02_uniquenes_of_slug(self):
        '''Test for uniqueness of slug.'''
        first_bk_cluster_slug = BaseKitCluster.query.first().slug
        self.db.session.add(
            BaseKitCluster(name="BaseKit Cluster Test", slug=str(first_bk_cluster_slug), description='Slug testing error',
                           api_url='http://www.admin_test.com', provisioning_enabled=False))
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, 'Test for checking uniqueness of slug failed'

    def test_03_for_repr(self):
        '''Test the __repr__ of BaseKitCluster model.'''
        first_bk_cluster = BaseKitCluster.query.first()
        assert "<BaseKitCluster('" + str(first_bk_cluster.id) + "', '" + \
            first_bk_cluster.slug + \
            "')>" in first_bk_cluster.__repr__(
            ), "Test for BaseKitCluster __repr__ failed"

    def test_04_entry_of_custom_slug(self):
        '''Test the entry of custom slug.'''
        self.db.session.add(
            BaseKitCluster(name="BaseKit Test Slug", slug='my_custom_slug_087', description='custom clug', api_url='http://www.admin_test.com'))
        self.db.session.commit()
        custom_slug_bk_cluster = BaseKitCluster.query.filter_by(
            slug='my_custom_slug_087').first()
        assert custom_slug_bk_cluster, 'Test for checking entry of custom slug failed'

    def test_05_for_default_provisioning(self):
        '''Test the default provisioning_enabled.(True)'''
        self.db.session.add(
            BaseKitCluster(name="BaseKit Test 124", api_url='http://www.admin_test.com'))
        self.db.session.commit()
        bk_cluster_provisioning = BaseKitCluster.query.filter_by(
            slug='basekit-test-124').first().provisioning_enabled
        assert bk_cluster_provisioning, "Test for checking default provisioning enabled failed"

    def test_06_get_the_inherited_class(self):
        ''' Check the inherited SluggableModel model class. '''
        baskekit_cluster = BaseKitCluster()
        assert isinstance(baskekit_cluster, SluggableModel), "Test to check inheritance from SluggableModel failed"

    def test_07_for_bkcluster_updation(self):
        ''' Check the BaseKitCluster updation. '''
        ''' Check the BaseKitCluster created_at and updated_at field. '''
        first_bk_cluster = BaseKitCluster.query.first()
        first_bk_cluster_created_at = first_bk_cluster.created_at
        first_bk_cluster_updated_at = first_bk_cluster.updated_at
        time.sleep(1)
        self.db.session.merge(
            BaseKitCluster(id=first_bk_cluster.id, name='Changed Cluster name119', description='updated_description'))
        try:
            self.db.session.commit()
            first_bk_cluster = BaseKitCluster.query.first()
            assert first_bk_cluster_created_at == first_bk_cluster.created_at, 'Test for checking whether "created_at" is not changing failed'
            assert first_bk_cluster_updated_at != first_bk_cluster.updated_at, 'Test for checking whether "updated_at" changes failed'
            assert True
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitCluster fields failed')
