# -*- coding: utf-8 -*-
from tests.models_tests import ModelsTestBase
from models.core import Service
from sqlalchemy.exc import IntegrityError
import time


class TestServiceModels(ModelsTestBase):

    def test_01_populate(self):
        self.db.session.add(
            Service(name='Test Service', provisioning_enabled=True, slug=None))
        self.db.session.add(
            Service(name='Another Service', provisioning_enabled=True, slug='custom-slug'))
        self.db.session.add(
            Service(name='Wrong Service', provisioning_enabled=False, slug=None))
        self.db.session.commit()
        assert Service.query.count() == 3

    def test_02_service_repr(self):
        ''' Test for repr for entries from test_01_populate '''
        fs = Service.query.first()
        assert 'Service' in repr(fs), "repr is %s" % fs

    def test_03_service_provision(self):
        ''' Test for provisioning_enabled '''
        self.db.session.add(
            Service(name='New Service', provisioning_enabled=True, slug=None))
        self.db.session.commit()
        assert Service.query.filter_by(
            slug='new-service').first().provisioning_enabled is True, "Test for adding service with 'provision_enabled' as True failed"

    def test_04_service_without_slug(self):
        '''Inserting into model without a slug'''
        self.db.session.add(Service(name='No Slug Service', provisioning_enabled=True, slug=None))
        self.db.session.commit()
        assert Service.query.filter_by(slug='no-slug-service').first(
        ), 'Tests for inserting into model without slug failed'

    def test_05_service_with_custom_slug(self):
        '''Inserting into model with a custom slug '''
        self.db.session.add(
            Service(name='Custom Slug Service', provisioning_enabled=True, slug='slug-telling-something'))
        self.db.session.commit()
        assert Service.query.filter_by(slug='slug-telling-something').first(
        ), 'Tests for inserting into model with custom slug failed'

    def test_06_service_with_duplicate_slug(self):
        '''Inserting into model with a duplicate slug (error)'''
        self.db.session.add(Service(name='Best Service', slug='test-service'))
        try:
            self.db.session.commit()
        except:
            self.db.session.rollback()
            assert IntegrityError, 'Test for slug duplication failed'

    def test_07_service_with_provisioning_disabled(self):
        '''Inserting into the model with provisioning_enabled turned False'''
        self.db.session.add(
            Service(name='Dead Service', provisioning_enabled=False))
        self.db.session.commit()
        assert Service.query.filter_by(slug='dead-service').first().provisioning_enabled is False, \
            'Test for disabled provisioning failed'

    def test_08_service_with_default_provisioning(self):
        '''Inserting into model without provisioning_enabled(default-True)'''
        self.db.session.add(Service(name='Default Service'))
        self.db.session.commit()
        assert Service.query.filter_by(slug='default-service').first().provisioning_enabled is True, \
            'Test for default provisioning_enabled failed'

    def test_09_update_provisioning_enabled_of_a_created_entry(self):
        '''Test for updating 'provisioning_enabled' of a service'''
        self.db.session.add(
            Service(name='New Service', provisioning_enabled=False, slug='my-new-service'))
        self.db.session.commit()
        service = Service.query.filter_by(slug='my-new-service').first()
        self.db.session.merge(
            Service(id=service.id, provisioning_enabled=True)
        )
        self.db.session.commit()
        assert Service.query.filter_by(slug='my-new-service').first().provisioning_enabled is True, \
            'Test for updating "provisioning enabled" of a Service failed'

    def test_10_update_slug_of_a_created_entry(self):
        '''Test for updating to duplicare 'slug' of a service - IntegrityError'''
        self.db.session.add(
            Service(name='Jetlaunch Service', provisioning_enabled=False, slug=None))
        self.db.session.add(
            Service(name='Create Domain Service', provisioning_enabled=False, slug=None))
        self.db.session.commit()
        service = Service.query.filter_by(slug='jetlaunch-service').first()
        self.db.session.merge(
            Service(id=service.id, slug='create-domain-service')
        )
        try:
            self.db.session.commit()
        except:
            self.db.session.rollback()
            assert IntegrityError, 'Test for error generation while updating to duplicate slug failed'

    def test_11_for_checking_created_at(self):
        '''Test for checking created_at '''
        for service in Service.query.all():
            assert service.created_at is not None
        self.db.session.add(
            Service(name='Site Service', provisioning_enabled=True, slug=None))
        self.db.session.commit()
        service = Service.query.filter_by(slug='site-service').first()
        service_created_at = service.created_at
        self.db.session.merge(
            Service(id=service.id, name='Site Service_renamed')
        )
        self.db.session.commit()
        updated_service = Service.query.filter_by(slug='site-service').first()
        assert service_created_at == updated_service.created_at, "Test for checking Service 'created_at' failed"

    def test_12_checking_updated_at(self):
        '''Test for checking updated_at '''
        for service in Service.query.all():
            assert service.updated_at is not None
        self.db.session.add(
            Service(name='Site Service_2', provisioning_enabled=True, slug=None))
        self.db.session.commit()
        service = Service.query.filter_by(slug='site-service_2').first()
        service_updated_at = service.updated_at
        time.sleep(1)
        self.db.session.merge(
            Service(id=service.id, name='Site Service_2_renamed')
        )
        self.db.session.commit()
        updated_service = Service.query.filter_by(
            slug='site-service_2').first()
        assert service_updated_at != updated_service.updated_at, "Test for checking Service 'updated_at' failed"
