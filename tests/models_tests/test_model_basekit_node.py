
from tests.api_tests import APITestBase
from tests.models_tests import ModelsTestBase
from models.basekit import BaseKitNode, BaseKitCluster
import time


class TestBaseKitNodeModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        APITestBase.populate(self.db)

    def test_02_for_repr(self):
        '''Test the __repr__ of BaseKitNode model.'''
        first_bk_node = BaseKitNode.query.first()
        assert "<BaseKitNode('" + str(first_bk_node.id) + "', '" + first_bk_node.cname + "')>" in first_bk_node.__repr__(
        ), "Test for BaseKitNode __repr__ failed"

    def test_03_for_default_provisioning(self):
        '''Test the default provisioning_enabled.(True)'''
        cluster = BaseKitCluster.query.first()
        self.db.session.add(
            BaseKitNode(cluster=cluster, cname='foo.logon.com', ip='10.6.1.02', instance_count=1, max_instances=2))
        self.db.session.commit()
        bk_node_provisioning = BaseKitNode.query.filter_by(
            cname='foo.logon.com').first().provisioning_enabled
        assert bk_node_provisioning, "Test for checking default provisioning enabled failed"

    def test_04_get_the_inherited_class(self):
        ''' Check the inherited BaseModel model class. '''
        from models.common import BaseModel
        baskekit_node = BaseKitNode()
        assert isinstance(
            baskekit_node, BaseModel), "Test to check inheritance from BaseModel failed"

    def test_05_for_bk_node_updation(self):
        ''' Check the BaseKitNode updation. '''
        first_bk_node = BaseKitNode.query.first()
        my_node_created_at = first_bk_node.created_at
        my_node_updated_at = first_bk_node.updated_at
        time.sleep(1)
        self.db.session.merge(
            BaseKitNode(id=first_bk_node.id, cname='foo.example.com', ip='10.6.1.102', instance_count=2, max_instances=4))
        try:
            self.db.session.commit()
            assert my_node_created_at == BaseKitNode.query.first().created_at, 'Test for checking whether "created_at" is not changing failed'
            assert my_node_updated_at != BaseKitNode.query.first().updated_at, 'Test for checking whether "updated_at" changes failed'
            assert True
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitNode fields failed')

    def test_06_for_basekit_node_fk_reference(self):
        '''Check the validity of FK reference to basekit_cluster'''
        my_bk_node = BaseKitNode.query.first()
        my_bk_cluster = my_bk_node.cluster
        cluster_nodes = BaseKitCluster.query.filter_by(id=my_bk_cluster.id).first().basekit_nodes
        assert my_bk_node in cluster_nodes, 'Test for checking the validity of FK reference to basekit_cluster failed'
