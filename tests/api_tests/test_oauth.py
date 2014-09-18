# -*- coding: utf-8 -*-
from flask import g
import json
import restkit.oauth2 as oauth
import time
from formencode.validators import String, UnicodeString

from tests.api_tests import APITestBase
from test_models.core import Partner, Language, Customer, PartnerAPIKey
from tests import dbhelper
from hoops.restful import Resource
from hoops.response import APIResponse
import hoops
import hoops.status
from test_models import db
from hoops import create_api, register_views
from hoops.base import APIResource, parameter
from hoops.generic import ListOperation, CreateOperation

print db

class OAuthEndpoint(Resource):
    def get(self):
        return APIResponse({
            "partner_id": g.partner.id,
            "api_key_id": g.api_key.id
        })

    def put(self):
        return APIResponse({
            "partner_id": g.partner.id,
            "api_key_id": g.api_key.id
        })

    def post(self):
        return APIResponse({
            "partner_id": g.partner.id,
            "api_key_id": g.api_key.id
        })

    def delete(self):
        return APIResponse({
            "partner_id": g.partner.id,
            "api_key_id": g.api_key.id
        })


class CustomerAPI(APIResource):
    route = "/oauth_customers"
    object_route = "/oauth_customers/<string:customer_id>"
    object_id_param = 'customer_id'
    model = Customer
    read_only = False


@CustomerAPI.method('list')
@parameter('include_suspended', String, "Include Suspended", False, False)
@parameter('include_inactive', String, "Include Inactive", False, False)
@parameter('limit_to_partner', String, "Limit to partner", False, False)
class ListCustomers(ListOperation):
    pass


@CustomerAPI.method('create')
@parameter('my_identifier', UnicodeString(max=64, if_missing=None), "Unique identifier of the customer in your database")
@parameter('name', UnicodeString(max=64, if_missing=None), "Customer name for your reference")
class CreateCustomer(CreateOperation):
    pass


class TestOAuth(APITestBase):
    @classmethod
    def get_app(cls):
        cls.db = db

        oauth_args = {'consumer_key': None,
                      'consumer_secret': None,
                      'token': None,
                      'token_secret': None}
        cls.api, app = create_api(database=db,
                                  flask_conf={'DEBUG': True,
                                              'ENVIRONMENT_NAME': 'test'},
                                  oauth_args=oauth_args)

        register_views()
        return app

    @classmethod
    def setup_app(cls):
        super(TestOAuth, cls).setup_app()
        cls.db.session.expire_on_commit = False
        hoops.flask.config['TESTING_PARTNER_API_KEY'] = None
        hoops.api.add_resource(OAuthEndpoint, '/oauthed', endpoint='oauthed')

        cls.language = Language.query.first()
        cls.partner = dbhelper.add(
            Partner(language=cls.language, name='test', output_format='json'),
            db=cls.db)
        cls.key = dbhelper.add(cls.partner.generate_api_key('test'), db=cls.db)
        cls.db.session.refresh(cls.key)
        cls.db.session.refresh(cls.partner)
        hoops.api.set_partner(cls.key)

    def test_oauth_get(self):
        """OAuth succeeds for GET requests"""
        self.oauth_call('GET', 'oauthed', 'query_string')
        self.oauth_call('GET', 'oauthed', 'header')

    def test_oauth_none(self):
        """Test without credentials"""
        self.validate(self.app.get('/oauthed'), hoops.status.library.API_AUTHENTICATION_REQUIRED)

    # OAuth library doesnt verify consumer keys
    # def test_oauth_invalid_consumer_key(self):
    #     """Test with bad consumer key"""
    #     # from oauth.signature_method.hmac_sha1 import OAuthSignatureMethod_HMAC_SHA1

    #     token = oauth.Token(key=self.key.token, secret=self.key.token_secret)
    #     consumer = oauth.Consumer(key='INVALID', secret=self.key.consumer_secret)
    #     params = {
    #         'oauth_version': "1.0",
    #         'oauth_nonce': oauth.generate_nonce(),
    #         'oauth_timestamp': int(time.time()),
    #         'oauth_token': token.key,
    #         'oauth_consumer_key': "INVALID",
    #     }

    #     req = oauth.Request(method='GET', url=self.url_for('oauthed', _external=True), parameters=params)
    #     signature_method = oauth.SignatureMethod_HMAC_SHA1()
    #     req.sign_request(signature_method, consumer, token)
    #     headers = req.to_header()
    #     self.validate(self.app.get(self.url_for('oauthed'), headers=headers), hoops.status.library.API_UNKNOWN_OAUTH_CONSUMER_KEY)

    def test_oauth_post(self):
        """OAuth succeeds for POST requests"""
        self.oauth_call('POST', 'oauthed', 'post')
        self.oauth_call('POST', 'oauthed', 'header')

    def test_oauth_put(self):
        """OAuth succeeds for PUT requests"""
        self.oauth_call('PUT', 'oauthed', 'post')
        self.oauth_call('PUT', 'oauthed', 'header', content_type='application/json', data=json.dumps({"test": 1}))
        self.oauth_call('PUT', 'oauthed', 'header', data='test=123')

    def test_oauth_delete_querystring(self):
        """OAuth succeeds for DELETE requests using query string"""
        self.oauth_call('DELETE', 'oauthed', 'query_string', fail=False)

    def test_oauth_delete_header(self):
        """OAuth succeeds for DELETE requests using header"""
        self.oauth_call('DELETE', 'oauthed', 'header', fail=False)

    def test_oauth2_emulate_restkit(self):
        token = oauth.Token(key=self.key.token, secret=self.key.token_secret)
        consumer = oauth.Consumer(key=self.key.consumer_key, secret=self.key.consumer_secret)
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_token': token.key,
            'oauth_consumer_key': consumer.key,
        }
        req = oauth.Request(method='GET', url=self.url_for('oauthed', _external=True), parameters=params)
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, token)
        headers = req.to_header()
        rv = self.app.get(self.url_for('oauthed'), headers=headers)
        data = json.loads(rv.data)

        assert data.get('status_code') == 1000, \
            "Expected successful authentication, got: %s " % rv.data
        assert data.get('response_data').get('partner_id') == self.partner.id
        assert data.get('response_data').get('api_key_id') == self.key.id

    def test_oauth_missing_parameter(self):
        token = oauth.Token(key=self.key.token, secret=self.key.token_secret)
        consumer = oauth.Consumer(key=self.key.consumer_key, secret=self.key.consumer_secret)
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_token': token.key,
            'oauth_consumer_key': consumer.key,
        }
        req = oauth.Request(method='GET', url=self.url_for('oauthed', _external=True), parameters=params)
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        del req['oauth_timestamp']
        req.sign_request(signature_method, consumer, token)
        rv = self.app.get(self.url_for('oauthed', **req))
        json.loads(rv.data)

        # Expecting API_MISSING_PARAMETER
        # expecting = hoops.status.library.get('API_MISSING_PARAMETER', parameter='none')

        # assert data.get('status_code') == expecting.status_code, "Wanted %d got %d" % (expecting.status_code, data.get('status_code'))

    def test_oauth_expired_timestamp(self):
        token = oauth.Token(key=self.key.token, secret=self.key.token_secret)
        consumer = oauth.Consumer(key=self.key.consumer_key, secret=self.key.consumer_secret)
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()) - 900,
            'oauth_token': token.key,
            'oauth_consumer_key': consumer.key,
        }
        req = oauth.Request(method='GET', url=self.url_for('oauthed', _external=True), parameters=params)
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, token)
        rv = self.app.get(self.url_for('oauthed', **req))
        data = json.loads(rv.data)

        # Expecting API_MISSING_PARAMETER
        expecting = hoops.status.library.API_EXPIRED_TIMESTAMP

        assert data.get('status_code') == expecting.status_code, "Wanted %d got %d" % (expecting.status_code, data.get('status_code'))

    def test_oauth_unexpected_sig_type(self):
        token = oauth.Token(key=self.key.token, secret=self.key.token_secret)
        consumer = oauth.Consumer(key=self.key.consumer_key, secret=self.key.consumer_secret)
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_token': token.key,
            'oauth_consumer_key': consumer.key,
        }
        req = oauth.Request(method='GET', url=self.url_for('oauthed', _external=True), parameters=params)
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, token)
        req['oauth_signature_method'] = 'plain'
        rv = self.app.get(self.url_for('oauthed', **req))
        data = json.loads(rv.data)

        # Expecting API_MISSING_PARAMETER
        expecting = hoops.status.library.API_UNEXPECTED_OAUTH_SIGNATURE_METHOD

        assert data.get('status_code') == expecting.status_code, "Wanted %d got %d" % (expecting.status_code, data.get('status_code'))

    def test_oauth_corrupted_token_secret(self):
        """OAuth fails for incorrect token_secret"""
        orig_key = self.key

        class fake(object):
            def __init__(self, **kwargs):
                for k in kwargs:
                    setattr(self, k, kwargs[k])

        self.key = fake(**vars(orig_key))
        self.key.token = orig_key.token
        self.key.token_secret = 'asdf'
        try:
            self.oauth_call('GET', 'oauthed', 'query_string', fail=True)
            self.oauth_call('GET', 'oauthed', 'header', fail=True)
        finally:
            self.key = orig_key

    def test_get_base_query(self):
        """TTest get base query with limiting to current partner"""
        p1 = Partner.query.filter_by(id=self.key.partner_id).first()
        c1 = Customer(name="TestCustomer1", my_identifier="test_customer_300", partner=p1, status='active')
        self.db.session.add_all([c1])
        self.db.session.commit()
        out = self.oauth_call('GET', '/oauth_customers', 'query_string', fail=False, **{"include_suspended": 1, "include_inactive": 1, "limit_to_partner": 1})
        assert out["pagination"]["total"] == 1, 'found %s != expected %s' % (out["pagination"]["total"], 1)

    def test_create_customer(self):
        """OAuth succeeds for POST requests"""
        # self.oauth_call('POST', '/oauth_customers', 'post', fail=False, name='Test Customer 001', my_identifier='testcustomer001')
        pass

    def oauth_call(self, method, target, req_type='query_string', fail=False, **kwargs):

        with self._app.app_context():

            token = oauth.Token(key=self.key.token, secret=self.key.token_secret)
            consumer = oauth.Consumer(key=self.key.consumer_key, secret=self.key.consumer_secret)
            params = {
                'oauth_version': "1.0",
                'oauth_nonce': oauth.generate_nonce(),
                'oauth_timestamp': int(time.time()),
                'oauth_token': token.key,
                'oauth_consumer_key': consumer.key,
            }
            if req_type in ['query_string', 'post']:
                get_params = dict(params, **kwargs)
                req = oauth.Request(method=method.upper(), url=self.url_for(target, _external=True), parameters=get_params)
            else:
                req = oauth.Request(method=method.upper(), url=self.url_for(target, _external=True), parameters=params)
            signature_method = oauth.SignatureMethod_HMAC_SHA1()
            req.sign_request(signature_method, consumer, token)
            headers = req.to_header()

            method = getattr(self.app, method.lower())
            if req_type is 'query_string':
                url = self.url_for(target, **req)
                rv = method(self.url_for(target, **req))
            elif req_type is 'post':
                url = self.url_for(target, **req)
                rv = method(self.url_for(target, **req), data=kwargs)
            elif req_type is 'header':
                url = self.url_for(target)
                rv = method(url, headers=headers, **kwargs)
            data = json.loads(rv.data)

            if not fail:
                assert data.get('status_code') == 1000 or data.get('status_code') == 1004, \
                    "Expected successful authentication, got: %s " % rv.data
                if type(data.get('response_data')) is dict and target == '/oauthd':
                    assert data.get('response_data').get('partner_id') == self.key.partner_id
                    assert data.get('response_data').get('api_key_id') == self.key.id
            else:
                assert data.get('status_code') == 4303, \
                    "Expected unsuccessful authentication, got: %s " % rv.data
                assert not g.get('api_key')

            return data

    def token(self, keyobj):
        return {
            'oauth_token': getattr(keyobj, 'token'),
            'oauth_token_secret': getattr(keyobj, 'token_secret')
        }

    def consumer(self, keyobj):
        return {
            'oauth_consumer_key': getattr(keyobj, 'consumer_key'),
            'oauth_consumer_secret': getattr(keyobj, 'consumer_secret')
        }


class TestInvalidOAuth(APITestBase):

    @classmethod
    def get_app(cls):
        cls.db = db
        # print "### => ", db
        oauth_args = {'consumer_key': None,
                      'consumer_secret': None,
                      'token': None,
                      'token_secret': None}
        cls.api, app = create_api(database=db,
                                  flask_conf={'DEBUG': True,
                                              'ENVIRONMENT_NAME': 'test'},
                                  oauth_args=oauth_args)
        register_views()
        return app

    @classmethod
    def setup_app(cls):
        #APITestBase.setup_app()
        super(TestInvalidOAuth, cls).setup_app()
        cls.db.session.expire_on_commit = False
        hoops.flask.config['TESTING_PARTNER_API_KEY'] = None
        cls.language = Language.query.first()
        # print Language.query.first()
        cls.partner = dbhelper.add(
            Partner(language=cls.language, name='test', output_format='json', enabled=False),
            db=cls.db)
        cls.key = dbhelper.add(cls.partner.generate_api_key('test'), db=cls.db)
        cls.db.session.refresh(cls.key)
        cls.db.session.refresh(cls.partner)
        hoops.api.set_partner(cls.key)

    def test_invalid_partner(self):
        """Tests invalid partner"""
        pak = PartnerAPIKey.query.filter_by(partner_id=self.key.partner_id).first()
        pak.enabled = False
        hoops.api.set_partner(pak)

        with self._app.app_context():

            token = oauth.Token(key=self.key.token, secret=self.key.token_secret)
            consumer = oauth.Consumer(key=self.key.consumer_key, secret=self.key.consumer_secret)
            params = {
                'oauth_version': "1.0",
                'oauth_nonce': oauth.generate_nonce(),
                'oauth_timestamp': int(time.time()),
                'oauth_token': token.key,
                'oauth_consumer_key': consumer.key,
            }
            get_params = dict(params, **{"include_suspended": 1, "include_inactive": 1, "limit_to_partner": 1})
            req = oauth.Request(method='GET', url=self.url_for('/oauth_customers', _external=True), parameters=get_params)

            signature_method = oauth.SignatureMethod_HMAC_SHA1()
            req.sign_request(signature_method, consumer, token)
            rv = self.app.get(self.url_for('/oauth_customers', **req))
            data = json.loads(rv.data)
            assert data["status_code"] == 4304
