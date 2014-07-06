from tests.models_tests import ModelsTestBase
from tests import dbhelper
from models.core import User, Language, Partner, Customer
from models import db
from sqlalchemy.exc import IntegrityError


class TestHashableModels(ModelsTestBase):

    def test_00_init(self):
        assert User

    def test_01_populate(self):

        out = self.populate_helper(lang=True, partner='test', customers=['test'], users=[])
        lang = Language.query.first()
        partner = out['partner']
        customer = out['customers'][0]
        self._add(User(customer=customer, partner=partner, language=lang, my_identifier="User_1", password="abc123def"))
        self._add(User(customer=customer, partner=partner, language=lang, my_identifier="User_2", password="abc!@#def"))
        self._add(User(customer=customer, partner=partner, language=lang, my_identifier="User_3", password="no-change-password"))
        self._add(User(customer=customer, partner=partner, language=lang, my_identifier="User_disabled", password="123test", status='deleted'))

        assert customer.users.count() == 4, \
            'Found %d instances of User' % customer.users.count()

    def test_02_check_password(self):

        user = User.get_one(my_identifier='User_1')

        assert user.password != "abc123def", user.password

    def test_03_update_password(self):

        user = User.get_one(my_identifier='User_1')

        prevPasswordHash = user.password

        dbhelper.update(user, self.db, my_identifier='User_1', password='test')

        assert user.password != prevPasswordHash, user.password

    def test_04_update_instance(self):

        user = User.get_one(my_identifier='User_disabled')

        prevPasswordHash = user.password

        # Perform an update without changing the password
        dbhelper.update(user, self.db, my_identifier='User_updated', status='active')
        user = User.get_one(my_identifier='User_updated')

        assert prevPasswordHash == user.password, \
            "Passwords do not match... new=%s, old=%s" % (user.password, prevPasswordHash)

    def test_05_verify_password_hash(self):

        assert User.get_one(my_identifier='User_1').\
            is_valid_password('test'), "Updated password verification failed"
        assert not User.get_one(my_identifier='User_1').\
            is_valid_password('abc123def'), "Previous password matched"
        assert User.get_one(my_identifier='User_3').\
            is_valid_password("no-change-password"), "Password verification failed"
        assert User.get_one(my_identifier='User_updated').status != 'deleted'
        assert User.get_one(my_identifier='User_updated').\
            is_valid_password('123test'), "Password verification did not succeed for updated user"

    def test_my_identifier_constraint(self):
        dbhelper.add(Partner(name='test2', language=Language.query.first(), output_format='json'), db)
        p1, p2 = Partner.query.limit(2).all()
        c1 = p1.customers.first()
        c2 = dbhelper.add(Customer(partner=p2), db)
        dbhelper.add(User(partner=p1, my_identifier='test', customer=c1, language=Language.query.first()), db)
        dbhelper.add(User(partner=p1, my_identifier='test2', customer=c1, language=Language.query.first()), db)
        dbhelper.add(User(partner=p2, my_identifier='test', customer=c2, language=Language.query.first()), db)
        dbhelper.add(User(partner=p2, my_identifier='test2', customer=c2, language=Language.query.first()), db)
        try:
            dbhelper.add(User(partner=p2, my_identifier='test2', customer=c2, language=Language.query.first()), db)
            assert False, "Insert should have failed"
        except IntegrityError:
            pass

    def test_to_json(self):
        u = User.query.first()
        out = u.to_json()
        assert sorted(out.keys()) == ['created_at', 'customer_id', 'email', 'firstname', 'id', 'language', 'lastname', 'my_identifier', 'password', 'role', 'status', 'updated_at'], sorted(out.keys())
        assert out['language'] == 'en'
