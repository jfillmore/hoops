from models.basekit import BaseKitBrand, BaseKitUser
from models.core import User
import time
# from models.core import Language
from tests.models_tests import ModelsTestBase
from tests.api_tests import APITestBase

from sqlalchemy.exc import IntegrityError


class TestBaseKitUserModel(ModelsTestBase):

    def test_01_populate(self):
        ''' Populate the required Tables. '''
        APITestBase.populate(self.db)

    def test_02_for_fk_reference_to_basekit_brand(self):
        ''' Check the FK reference of BaseKitUser to BaseKitBrand.'''
        my_bk_user = BaseKitUser.query.first()
        my_bk_brand = my_bk_user.brand  # via backref
        bk_users_for_brand = BaseKitBrand.query.filter_by(
            id=my_bk_brand.id).first().basekit_users  # via relationship
        assert my_bk_user in bk_users_for_brand, "Test for checking the FK reference of BaseKitUser to BaseKitBrand failed"

    def test_03_for_fk_reference_to_user(self):
        ''' Check the FK reference of BaseKitUser to User. '''
        my_bk_user = BaseKitUser.query.first()
        my_user = my_bk_user.user  # via backref
        bk_users_for_user = User.query.filter_by(
            id=my_user.id).first().basekit_users  # via relationship
        assert my_bk_user in bk_users_for_user, "Test for checking the FK reference of BaseKitUser to User failed"

    def test_04_for_repr(self):
        '''Test the __repr__ of BaseKitUser model.'''
        first_bk_user = BaseKitUser.query.first()
        assert "<BaseKitUser('" + str(first_bk_user.id) + "')>" in first_bk_user.__repr__(
        ), "Test for BaseKitUser __repr__ failed"

    def test_05_for_unique_bk_user_id(self):
        '''Test the uniqueness of bk_user_id.'''
        my_bk_user_id = BaseKitUser.query.first().bk_user_id
        bk_brand = BaseKitBrand.query.first()
        user = User.query.first()
        self.db.session.add(
            BaseKitUser(brand=bk_brand, bk_user_id=my_bk_user_id, user=user))
        try:
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            assert IntegrityError, "Test for checking uniqueness of bk_user_id failed"

    def test_06_get_the_inherited_class(self):
        ''' Check the inherited BaseModel model class.'''
        from models.common import BaseModel
        baskekit_user = BaseKitUser()
        assert isinstance(
            baskekit_user, BaseModel), "Test to check inheritance of BaseKitUser from BaseModel failed"

    def test_07_for_bk_user_updation(self):
        ''' Check the BaseKitUser updation. '''
        first_bk_user = BaseKitUser.query.first()
        my_bk_user_created_at = first_bk_user.created_at
        my_bk_user_updated_at = first_bk_user.updated_at
        time.sleep(1)
        self.db.session.merge(
            BaseKitUser(id=first_bk_user.id, bk_user_id='500'))
        try:
            self.db.session.commit()
            assert my_bk_user_created_at == BaseKitUser.query.first().created_at, 'Test for checking whether "created_at" is not changing failed'
            assert my_bk_user_updated_at != BaseKitUser.query.first().updated_at, 'Test for checking whether "updated_at" changes failed'
            assert True
        except Exception, e:
            self.db.session.rollback()
            raise e('Test for updating the BaseKitUser fields failed')

