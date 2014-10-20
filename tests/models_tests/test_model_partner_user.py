# -*- coding: utf-8 -*-

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
from test_config import OutputFormat
from test_models.core import Language, Partner, PartnerUser
from hoops.utils import HashableModel
from tests.models_tests import ModelsTestBase
from tests import dbhelper
import time


class TestUserModels(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        lang_en = Language(lang='en', name="English")
        partner_1 = Partner(name='eNom_1', language=lang_en,
                            output_format=OutputFormat.JSON)
        partner_2 = Partner(name='eNom_2', language=lang_en,
                            output_format=OutputFormat.JSON)
        partner_3 = Partner(name='eNom_3', language=lang_en,
                            output_format=OutputFormat.JSON)
        partner_user_1 = PartnerUser(partner=partner_1, status='active',
                                     firstname="Charls", lastname='Mathew',
                                     email="jetlaunch588@gmail.com", password="nuventure", my_identifier="chm")
        partner_user_2 = PartnerUser(partner=partner_1, status='active',
                                     firstname="John", lastname='Stalin',
                                     email="jetlaunch588+1@gmail.com", password="jetlaunch", my_identifier="jet")
        partner_user_3 = PartnerUser(partner=partner_2, status='active',
                                     firstname="Shawn", lastname='Stephen',
                                     email="jetlaunch588+2@gmail.com", password="jetlaunch", my_identifier="jet1")

        self.db.session.add_all(
            [lang_en, partner_1, partner_2, partner_3])
        self.db.session.commit()

        partner_user_4 = PartnerUser(firstname='Roger', lastname='Haris', email='jetlaunch588+3@gmail.com', partner=Partner.query.first())
        self.db.session.add_all(
            [partner_user_1, partner_user_2, partner_user_3, partner_user_4])

        self.db.session.commit()

        assert Language.query.count() == 1
        assert Partner.query.count() == 3
        assert PartnerUser.query.count() == 4

    def test_02_partner_user_repr(self):
        ''' Check PartnerUser __repr__. '''
        partner_user = PartnerUser.query.first()
        assert str(partner_user.id) in repr(partner_user) \
            and partner_user.firstname in repr(partner_user) \
            and partner_user.lastname in repr(partner_user), \
            repr(partner_user)

    def test_03_default_status(self):
        ''' Check insert into the PartnerUser model without status (default: active). '''
        partner = Partner.query.filter_by(name='eNom_1').one()
        self.db.session.add(
            PartnerUser(partner=partner,
                        firstname="John", lastname='Stalin',
                        email="jetlaunch588+4@gmail.com",
                        password="jetlaunch",
                        my_identifier="jet4"))
        self.db.session.commit()
        my_user = PartnerUser.query.filter_by(email="jetlaunch588+4@gmail.com").first()
        assert 'active' in my_user.status, my_user.status

    def test_04_for_user_created_at(self):
        ''' Check the PartnerUser created_at field. '''
        my_user = PartnerUser.query.filter_by(email='jetlaunch588+1@gmail.com').first()
        user_created_at = my_user.created_at
        self.db.session.merge(
            PartnerUser(id=my_user.id, lastname='Jijo')
        )
        self.db.session.commit()
        my_user = PartnerUser.query.filter_by(email='jetlaunch588+1@gmail.com').first()
        assert user_created_at == my_user.created_at, my_user.created_at

    def test_05_for_user_updated_at(self):
        ''' Check the PartnerUser updated_at field. '''
        my_user = PartnerUser.query.filter_by(email="jetlaunch588@gmail.com").first()
        user_updated_at = my_user.updated_at
        time.sleep(1)
        self.db.session.merge(
            PartnerUser(id=my_user.id, password="test"))
        self.db.session.commit()
        my_user = PartnerUser.query.filter_by(email="jetlaunch588@gmail.com").first()
        assert user_updated_at != my_user.updated_at, 'Test for checking whether "updated_at" is not changing failed'

    def test_06_isinstance_HashableModel(self):
        ''' Check the inherited HashableModel class. '''
        user = PartnerUser()
        assert isinstance(
            user, HashableModel), "Test to check inheritance from HashableModel failed"

    def test_07_isinstance_UserMixin(self):
        ''' Check the inherited UserMixin class. '''
        user = PartnerUser()
        assert isinstance(
            user, UserMixin), "Test to check inheritance from UserMixin failed"

    def test_08_unique_constraint_email(self):
        ''' Ensure that the emailid and partner_id constraint work'''
        try:
            #email id 'jetlaunch588@gmail.com' was already inserted along with partner_id 1 in pouplate method.
            partner = Partner.query.filter_by(name='eNom_1').one()
            dbhelper.add(PartnerUser(partner=partner, status='active',
                                     firstname="Charls", lastname='Mathew',
                                     email="jetlaunch588@gmail.com", password="nuventure", my_identifier="chm1"), self.db)
            assert False, 'Duplicate email should have failed'
        except IntegrityError:
            pass

    def test_09_unique_constraint_my_identifier(self):
        ''' Ensure that my_identifer constraint work'''
        try:
            #my_identifier 'chm' was already inserted along with partner_id 1 in pouplate method.
            partner = Partner.query.filter_by(name='eNom_1').one()
            dbhelper.add(PartnerUser(partner=partner, status='active',
                                     firstname="Charls", lastname='Mathew',
                                     email="jetlaunch588@gmail.com", password="nuventure", my_identifier="chm"), self.db)
            assert False, 'Duplicate email should have failed'
        except IntegrityError:
            pass

    def test_10_get_the_partner_for_partner_user(self):
        ''' Check the foreign key validity of Partner. '''
        p = Partner.query.first()
        assert p.partner_users.all()[0].partner == p, "Test for checking validity of a partner for User failed"

    def test_11_get_the_property_name(self):
        ''' Check the @property name key of a PartnerUser. '''
        p = PartnerUser.query.first()
        assert p.name == p.firstname + ' ' + p.lastname, "assertion of the @property of PartnerUser failed"

    def test_is_active(self):
        p = PartnerUser.query.first()
        assert p.is_active()
