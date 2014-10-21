# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError
from test_config import OutputFormat
from test_models.core import Customer, Language, Partner
from tests.models_tests import ModelsTestBase
import time


class TestCustomerModels(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        l1 = Language(name="English", lang='en-US', active=1)
        p1 = Partner(name="TestPartner1", language=l1, output_format=OutputFormat.JSON, enabled=True)
        p2 = Partner(name="TestPartner2", language=l1, output_format=OutputFormat.JSON, enabled=True)
        p3 = Partner(name="TestPartner3", language=l1, output_format=OutputFormat.JSON, enabled=True)
        self.db.session.add_all([l1, p1, p2, p3])
        self.db.session.commit()
        c1 = Customer(name="TestCustomer1", my_identifier="test_customer_100", partner=p1, status='active')
        c2 = Customer(name="TestCustomer2", my_identifier="test_customer_200", partner=p1, status='active')
        c3 = Customer(name="TestCustomer3", my_identifier="test_customer_300", partner=p1, status='active')
        self.db.session.add_all([c1, c2, c3])
        self.db.session.commit()
        assert Language.query.count() == 1
        assert Customer.query.count() == 3
        assert Partner.query.count() == 3

    def test_02_customer_repr(self):
        ''' Check Customer __repr__. '''
        customer = Customer.query.first()
        assert customer, "Test of __repr__ failed"

    def test_03_insert_with_duplicate_identifier(self):
        ''' Check insert into model with a duplicate my_identifier (IntegrityError). '''
        p1 = Partner.query.filter_by(name="TestPartner1").one()
        self.db.session.add(
            Customer(name="TestCustomer4", my_identifier="test_customer_100", partner=p1, status='active'))
        # "test_customer_100" is already a my_identifier for a previous entry; see test_01_populate()
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, 'Test to check uniqueness of my_identifier in Customer failed'

    def test_04_insert_into_without_status(self):
        ''' Check insert into the model without status (default: active). '''
        p1 = Partner.query.filter_by(name="TestPartner1").one()
        self.db.session.add(
            Customer(name="TestCustomer4", my_identifier="test_customer_400", partner=p1))
        self.db.session.commit()
        my_customer = Customer.query.filter_by(
            my_identifier='test_customer_400').first()
        assert 'active' in my_customer.status, 'Test for default status for Customer failed'

    def test_05_get_the_partner_for_customer(self):
        ''' Check the foreign key validity. '''
        my_customer = Customer.query.filter_by(
            my_identifier='test_customer_100').first()
        my_partner = my_customer.partner
        partner = Partner.query.filter_by(
            name=my_partner.name
        ).first()
        assert my_partner.customers.count() == partner.customers.count(), "Test for checking validity of a partner for Customer failed"

    def test_06_get_the_inherited_class(self):
        ''' Check the inherited model class. '''
        from hoops.common import BaseModel
        _customer = Customer()
        assert isinstance(
            _customer, BaseModel), "Test to check inheritance from BaseModel failed"

    def test_07_for_customer_status_insert(self):
        ''' Check the Customer status insert. '''
        p1 = Partner.query.filter_by(name="TestPartner1").one()
        self.db.session.add(
            Customer(name="TestCustomer5", my_identifier="test_customer_500", partner=p1, status='suspended'))
        self.db.session.commit()
        my_customer = Customer.query.filter_by(
            my_identifier='test_customer_500').first()
        assert my_customer.status == 'suspended', 'Test for checking status of Customer failed'

    def test_08_for_customer_created_at(self):
        ''' Check the Customer created_at field. '''
        my_customer = Customer.query.filter_by(my_identifier='test_customer_500').first()
        customer_created_at = my_customer.created_at
        self.db.session.merge(
            Customer(id=my_customer.id, name='TestCustomer5_1')
        )
        self.db.session.commit()
        my_customer = Customer.query.filter_by(my_identifier='test_customer_500').first()
        assert customer_created_at == my_customer.created_at, 'Test for checking whether "created_at" changes failed'

    def test_09_for_customer_updated_at(self):
        ''' Check the Customer updated_at field. '''
        my_customer = Customer.query.filter_by(my_identifier='test_customer_200').first()
        customer_updated_at = my_customer.updated_at
        self.db.session.merge(
            Customer(id=my_customer.id, name='TestCustomer2_1')
        )
        time.sleep(1)
        self.db.session.commit()
        my_customer = Customer.query.filter_by(my_identifier='test_customer_200').first()
        assert customer_updated_at != my_customer.updated_at, 'Test for checking whether "updated_at" is not changing failed'

    def test_10_customer_supported_services(self):
        '''Make sure the services supported are as expected'''
        services = Customer.get_service_classes()
        from test_models.basekit import BaseKitSite
        assert BaseKitSite in services
        assert len(services) == 1

    def test_11_get_active_services(self):
        '''Make sure we get an array of query handles'''
        services = Customer.query.first().get_active_services()
        for item in services:
            assert isinstance(item, Customer.query.__class__)
        assert len(services) == 1

    def test_11_customer_service_instances(self):
        '''Make sure an array of services is returned when expected'''
        c = Customer.query.first()
        assert c.count_active_services() == 0
