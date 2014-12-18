
from sqlalchemy.exc import IntegrityError
from test_models.basekit import BaseKitSite, BaseKitDomain
from hoops.common import BaseModel
from tests.models_tests import ModelsTestBase
from tests.api_tests import APITestBase
import time


class TestBaseKitDomainModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        APITestBase.populate(self.db)
        self.db.session.add(BaseKitDomain(site_id=BaseKitSite.query.first().id, bk_domain_id=123, domain='bkreseller.com'))
        self.db.session.commit()

    def test_02_for_fk_reference_to_basekit_site(self):
        ''' Check the FK reference of BaseKitDomain to BaseKitSite.'''
        my_bk_domain = BaseKitDomain.query.first()
        my_bk_site = my_bk_domain.site  # via backref
        bk_domains_for_site = BaseKitSite.query.filter_by(
            id=my_bk_site.id).first().basekit_domains  # via relationship
        assert my_bk_domain in bk_domains_for_site, "Test for checking the FK reference of BaseKitSite to BaseKitDomain failed"

    def test_03_for_repr(self):
        '''Test the __repr__ of BaseKitDomain model.'''
        first_bk_site = BaseKitDomain.query.first()
        assert "<BaseKitDomain('" + str(first_bk_site.id) + "')>" in first_bk_site.__repr__(
        ), "Test for BaseKitDomain __repr__ failed"

    def test_04_for_unique_bk_domain_id(self):
        '''Test the uniqueness of bk_domain_id.'''
        my_bk_domain_id = BaseKitDomain.query.first().bk_domain_id
        site = BaseKitSite.query.first()
        self.db.session.add(
            BaseKitDomain(site=site, bk_domain_id=my_bk_domain_id, domain="google.com"))
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, "Test for checking uniqueness of bk_domain_id failed"

    def test_05_for_bk_domain_updation(self):
        ''' Check the BaseKitDomain updation.'''
        first_bk_domain = BaseKitDomain.query.first()
        my_bk_domain_created_at = first_bk_domain.created_at
        my_bk_domain_updated_at = first_bk_domain.updated_at
        site = BaseKitSite.query.first()
        time.sleep(1)
        self.db.session.merge(
            BaseKitDomain(id=first_bk_domain.id, site_id=site.id, bk_domain_id='4', domain="wiki.com"))
        try:
            self.db.session.commit()
            assert my_bk_domain_created_at == BaseKitDomain.query.first().created_at, 'Test for checking whether "created_at" is not changing failed'
            assert my_bk_domain_updated_at != BaseKitDomain.query.first().updated_at, 'Test for checking whether "updated_at" changes failed'
            assert True
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitDomain fields failed')

    def test_07_get_the_inherited_class(self):
        ''' Check the inherited BaseModel model class.'''
        baskekit_domain = BaseKitDomain()
        assert isinstance(
            baskekit_domain, BaseModel), "Test to check inheritance of BaseKitDomain from BaseModel failed"

    def test_08_for_to_api_response(self):
        ''' Check the to_api_response method of BaseKitDomain '''
        bk_domain_data = BaseKitDomain.query.first().to_json()
        assert type(bk_domain_data) == dict, "Test to check to_api_response failed"
