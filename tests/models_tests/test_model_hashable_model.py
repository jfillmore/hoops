import unittest
from sqlalchemy import event
from sqlalchemy import Column, String
from coaster.sqlalchemy import BaseMixin

from hoops.common import HashedPasswordMixin, HashUtils
from hoops import db

from tests.models_tests import ModelsTestBase


class BaseModel(BaseMixin, db.Model):
    """ Abstract class based on db.Model which should be used to define other
    models. This will contain the common implementation details for those
    classes.
    """
    __abstract__ = True


class HashableModel(BaseModel, HashedPasswordMixin):
    """ Model class which extends the HashedPasswordMixin behavior to BaseModel class. All
    model which require password hashing feature should inherit from this model.
    """
    __abstract__ = True


event.listen(HashableModel, 'before_insert', HashUtils.hash_password_before_change_listener, propagate=True)
event.listen(HashableModel, 'before_update', HashUtils.hash_password_before_change_listener, propagate=True)


class TheTestHashableModel(HashableModel):
    """Test model for HashableModel"""
    __tablename__ = 'test_hashable_model'
    __hash_attribute__ = "password"

    username = Column(String(80), unique=True)
    password = Column(String(255), nullable=True)

    @classmethod
    def add(cls, username, password):
        """Insert data to TheTestHashableModel"""
        errorcode = None
        db.session.add(TheTestHashableModel(username=username, password=password))
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            errorcode = str(e)
        return errorcode

    @classmethod
    def get(cls, username):
        return TheTestHashableModel.query.filter(TheTestHashableModel.username == username).first()


class TestCommonModels(ModelsTestBase, unittest.TestCase):

    def test_00_init(self):
        assert TheTestHashableModel

    def test_01_populate(self):

        # Add TheTestHashableModel instances
        TheTestHashableModel.add(username="TestHashUser_1", password="abc123def")
        TheTestHashableModel.add(username="TestHashUser_2", password="abc!@#def")
        TheTestHashableModel.add(username="TestHashUser_3", password="no-change-password")

        assert TheTestHashableModel.query.count() == 3

    def test_06_check_hex_digest(self):

        setattr(TheTestHashableModel, 'enabled', True)
        assert not TheTestHashableModel.get(username='TestHashUser_1').is_valid_password('abcdef123'), "Password Mismatch"
        del TheTestHashableModel.enabled
        assert TheTestHashableModel.get(username='TestHashUser_1').is_valid_password('abc123def'), "Invalid Password matched"
        assert not TheTestHashableModel.get(username='TestHashUser_2').is_valid_password('abcdef!@#'), "Password Mismatch"
        assert TheTestHashableModel.get(username='TestHashUser_3').is_valid_password('no-change-password'), "Password not hashed properly"

    def test_07_no_password(self):

        m = TheTestHashableModel(username="TestHashUser_4")
        db.session.add(m)
        db.session.commit()
        assert not m.is_valid_password('')
        assert not m.is_valid_password('test')

    def test_08_blank_password(self):

        m = TheTestHashableModel(username="TestHashUser_5", password='')
        db.session.add(m)
        db.session.commit()
        assert not m.is_valid_password('')
        assert not m.is_valid_password('test')
