from flask import g
from formencode.validators import String, Int
from hoops.status import library
from hoops.base import APIOperation, APIModelOperation, APIResource, parameter, url_parameter
from hoops.generic import ListOperation, RetrieveOperation, NotSpecified
from tests.api_tests import APITestBase

from test_models.core import Customer, Partner, Language, Package, CustomerPackage, User
from hoops.exc import APIException
from hoops.utils import find_subclasses


@parameter('test', String, "test")
@url_parameter('test_id', String, "test")
class test_resource(APIResource):
    route = "/test"
    object_route = '/test/<test_id>'
    object_id_param = 'test_id'
    read_only = True


@test_resource.method('retrieve')
class RetreiveTest(APIOperation):
    pass


@test_resource.method('list')
class ListTest(APIOperation):
    pass


@url_parameter('customer_id', Int, "test")
class test_model(APIResource):
    route = "/cust"
    object_route = "/cust/<string:customer_id>"
    object_id_param = 'customer_id'
    model = Customer
    read_only = False


@test_model.method('retrieve', 'customer')
class CustRetreiveTest(APIModelOperation):
    pass


@test_model.method('update')
class CustPutTest(APIModelOperation):
    pass


class CustomerAPI(APIResource):
    route = "/customers"
    object_route = "/customers/<string:customer_id>"
    object_id_param = 'customer_id'
    model = Customer
    read_only = False


@CustomerAPI.method('list')
@parameter('include_suspended', String, "Include Suspended", False, False)
@parameter('include_inactive', String, "Include Inactive", False, False)
class ListCustomers(ListOperation):
    pass


@CustomerAPI.method('retrieve')
@url_parameter('customer_id', Int, "Customer ID")
class RetrieveCustomer(RetrieveOperation):
    id_column = 'id'


class TestBaseClasses(APITestBase):

    def test_api_operation(self):
        """Test the basics of the APIOperation class"""
        with self._app.test_request_context():
            op = APIOperation(resource=APIResource())
            assert not hasattr(op, 'url_params')
            assert not hasattr(op, 'params')
            op()
            assert hasattr(op, 'url_params')
            assert hasattr(op, 'params')

            def test_setup(*args, **kwargs):
                op.okay = True
            op.setup = test_setup
            op()
            assert hasattr(op, 'okay')
        print find_subclasses('Invalid class')

    def test_combined_params(self):
        """Test combined_params"""
        @parameter('person_id', Int, "test")
        class test_res(APIResource):
            pass

        @parameter('customer_id', Int, "test")
        @test_res.method('list')
        class test_op(APIOperation):
            pass

        op = test_op(resource=test_res())
        with self._app.test_request_context("/foo?customer_id=1&person_id=1"):
            op()

        op.params = {"test": 1}
        op.url_params = {"test2": 2}
        assert 'test' in op.combined_params
        assert 'test2' in op.combined_params

    def test_validation(self):
        """Test validation works"""
        rv = self.app.get("/test/Yup?test=Works")
        self.validate(rv, library.API_OK)

    def test_validate_failure(self):
        """Test validation failure works"""
        rv = self.app.get("/test/Yup?nope=Failed")
        self.validate(rv, library.API_INPUT_VALIDATION_FAILED)
        rv = self.app.get("/cust/Nope")
        self.validate(rv, library.API_INPUT_VALIDATION_FAILED)
        rv = self.app.get("/test/Nope")
        self.validate(rv, library.API_INPUT_VALIDATION_FAILED)

    def test_model_op(self):
        """Test APIModelOperation behaves as expected"""
        self.populate(use_db=self.db)
        partner = Partner.query.filter_by(name='dev').first()
        custid = partner.customers.first().id
        with self._app.test_request_context("/cust/%s" % custid):
            g.partner = partner
            g.api_key = partner.api_keys.first()
            op = CustRetreiveTest(resource=test_model())
            op(customer_id=custid)
            q = op.get_base_query()
            assert q.count(), q.count()
            item = op.load_object(customer_id=custid)
            assert item.id == custid

        with self._app.test_request_context("/cust/1231"):
            try:
                g.partner = partner
                g.api_key = partner.api_keys.first()
                op.url_params['customer_id'] = op.url_params['customer_id'] + 10
                obj = op.load_object()
                assert False, "Object load succeeded %s" % obj
            except APIException:
                assert True, "Object didn't load - good"

    def test_allops(self):
        """Test all endpoints trigger as expected within base (if not already tested)"""
        rv = self.app.put("/cust/123?test=OK")
        self.validate(rv, library.API_OK)
        rv = self.app.put("/cust")
        self.validate(rv, library.API_RESOURCE_NOT_FOUND)
        rv = self.app.put("/test/1")
        self.validate(rv, library.API_INVALID_REQUEST_METHOD)

        rv = self.app.post("/cust")
        self.validate(rv, library.API_CODE_NOT_IMPLEMENTED)

        rv = self.app.post("/cust/1223123313")
        self.validate(rv, library.API_RESOURCE_NOT_FOUND)
        rv = self.app.post("/test")
        self.validate(rv, library.API_INVALID_REQUEST_METHOD)

        rv = self.app.delete("/cust/3321")
        self.validate(rv, library.API_CODE_NOT_IMPLEMENTED)
        rv = self.app.delete("/cust")
        self.validate(rv, library.API_RESOURCE_NOT_FOUND)
        rv = self.app.delete("/test/1")
        self.validate(rv, library.API_INVALID_REQUEST_METHOD)

        rv = self.app.get("/cust")
        self.validate(rv, library.API_CODE_NOT_IMPLEMENTED)

    def test_route_registration(self):
        '''Verify auto-registration works by checking for a couple known routes'''
        assert '/cust/<string:customer_id>' in [rule.rule for rule in self._app.url_map.iter_rules()]
        # assert '/users' in [rule.rule for rule in self._app.url_map.iter_rules()]
        # assert '/users/<string:user_id>' in [rule.rule for rule in self._app.url_map.iter_rules()]

    def test_parameter_decorator(self):
        """Test @parameter decorator"""

        @parameter('first', String, "test")
        @parameter('second', String, "test")
        class Thing(object):
            pass

        @parameter('third', String, "test")
        class Thing2(Thing):
            pass

        # Test instnatiation
        t = Thing()
        t2 = Thing2()
        assert hasattr(t, 'schema')
        assert hasattr(t2, 'schema')

        # Check inheritance worked right
        assert 'first' in Thing.schema.fields
        assert 'second' in Thing.schema.fields
        assert 'third' not in Thing.schema.fields

        assert 'first' in Thing2.schema.fields
        assert 'second' in Thing2.schema.fields
        assert 'third' in Thing2.schema.fields

    def test_url_parameter_decorator(self):
        """Test @url_parameter decorator"""

        @url_parameter('first', String, "test")
        @url_parameter('second', String, "test")
        class Thing(object):
            pass

        @url_parameter('third', String, "test")
        class Thing2(Thing):
            pass

        # Test instnatiation
        t = Thing()
        t2 = Thing2()
        assert hasattr(t, 'url_schema')
        assert hasattr(t2, 'url_schema')

        # Check inheritance worked right
        assert 'first' in Thing.url_schema.fields
        assert 'second' in Thing.url_schema.fields
        assert 'third' not in Thing.url_schema.fields

        assert 'first' in Thing2.url_schema.fields
        assert 'second' in Thing2.url_schema.fields
        assert 'third' in Thing2.url_schema.fields

    def test_nonzero(self):
        ns = NotSpecified()
        assert repr(ns) == "<unspecified>"
        assert str(ns) == "<unspecified>"
        assert bool(ns) is False

    def test_get_base_query(self):
        """Tests the various permutations of include_inactive/include_suspended"""
        lang_en = Language.query.filter_by(lang='en').one()

        p2 = Partner(name='eNom_2', language=lang_en, output_format='json', slug=None)
        p3 = Partner(name='eNom_3', language=lang_en, output_format='json', slug=None)
        self.db.session.add_all([p2, p3])

        self.db.session.flush()
        p1 = Partner.query.first()

        c1 = Customer(name="TestCustomer1", my_identifier="test_customer_300", partner=p1, status='active')

        c7 = Customer(name="TestCustomer7", my_identifier="test_customer_700", partner=p1, status='active')
        self.db.session.add_all([
            c1,
            Customer(name="TestCustomer2", my_identifier="test_customer_200", partner=p2, status='active'),
            Customer(name="TestCustomer3", my_identifier="test_customer_100", partner=p1, status='suspended'),
            Customer(name="TestCustomer4", my_identifier="test_customer_400", partner=p1, status='active'),
            Customer(name="TestCustomer5", my_identifier="test_customer_500", partner=p2, status='active'),
            Customer(name="TestCustomer6", my_identifier="test_customer_600", partner=p1, status='deleted'),
            c7])

        pkg1 = Package(name="Test Package 001", enabled=1, partner=p1, description='test_package 0001')
        pkg2 = Package(name="Test Package 002", enabled=1, partner=p1, description='test_package 002')
        pkg3 = Package(name="Test Package 003", enabled=0, partner=p1, description='test_package 003')

        self.db.session.add_all([
            pkg1, pkg2, pkg3,
            CustomerPackage(package=pkg1, status='active', customer=c1),
            CustomerPackage(package=pkg2, status='active', customer=c1),
            CustomerPackage(package=pkg3, status='disabled', customer=c1),
            CustomerPackage(package=pkg3, status='active', customer=c7),

            User(customer=c1, partner=p1, status='active', firstname='user',
                 lastname='test_1', language=lang_en, email='me@me.com', password='test1', my_identifier='test001'),
            User(customer=c1, partner=p1, status='active', firstname='user2',
                 lastname='test_2', language=lang_en, email='me_2@me.com', password='test2', my_identifier='test002'),
            User(customer=c1, partner=p1, status='disabled', firstname='user3',
                 lastname='test_3', language=lang_en, email='me_3@me.com', password='test3', my_identifier='test003')
        ])

        self.db.session.commit()
        customer_id = c1.id

        table = (
            ({}, 5),
            ({"include_suspended": 1}, 6),
            ({"include_inactive": 1}, 6),
            ({"include_suspended": 1, "include_inactive": 1}, 7),
        )
        for trial in table:
            url = self.url_for('/customers', **trial[0])
            rv = self.app.get(url)
            out = self.validate(rv, library.API_OK)
            assert out["pagination"]["total"] == trial[1], 'found %s != expected %s for %s' % (out["pagination"]["total"], trial[1], trial[0])

        url = self.url_for('/customers', page=3)
        rv = self.app.get(url)
        out = self.validate(rv, library.get('API_VALUE_TOO_HIGH', value='page'))

        url = self.url_for('/customers', customer_id=customer_id)
        rv = self.app.get(url)
        out = self.validate(rv, library.API_OK)
        assert customer_id == out['response_data']['id']
