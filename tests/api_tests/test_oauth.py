# -*- coding: utf-8 -*-

from tests.api_tests import APITestBase
from test_models.core import Partner, Language
from tests import dbhelper
from flask import g
import json
import restkit.oauth2 as oauth
import time
from hoops.restful import Resource
from hoops.response import APIResponse
import hoops
import hoops.status
from test_models import db
from hoops import create_api, register_views


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


class TestOAuth(APITestBase):
    @classmethod
    def get_app(cls):
        cls.db = db
        cls.api, app = create_api(database=db,
                                  flask_conf={'DEBUG': True,
                                              'ENVIRONMENT_NAME': 'test'},
                                  oauth_args={'apikey': 'dummy_key'})
        register_views()
        return app

    @classmethod
    def setup_app(cls):
        super(TestOAuth, cls).setup_app()
        hoops.flask.config['TESTING_PARTNER_API_KEY'] = None
        hoops.api.add_resource(OAuthEndpoint, '/oauthed', endpoint='oauthed')

        cls.language = Language.query.first()
        cls.partner = dbhelper.add(
            Partner(language=cls.language, name='test', output_format='json'),
            db=cls.db)
        cls.key = dbhelper.add(cls.partner.generate_api_key('test'), db=cls.db)
        cls.db.session.refresh(cls.key)
        cls.db.session.refresh(cls.partner)

    def test_oauth_get(self):
        """OAuth succeeds for GET requests"""
        self.oauth_call('GET', 'oauthed', 'query_string')
        self.oauth_call('GET', 'oauthed', 'header')

    def test_oauth_none(self):
        """Test without credentials"""
        self.validate(self.app.get('/oauthed'), hoops.status.library.API_AUTHENTICATION_REQUIRED)

    def test_oauth_invalid_consumer_key(self):
        """Test with bad consumer key"""
        self.validate(self.app.get(self.url_for('oauthed', oauth_consumer_key='invalid')), hoops.status.library.API_UNKNOWN_OAUTH_CONSUMER_KEY)

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
        data = json.loads(rv.data)

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
            req = oauth.Request(method=method.upper(), url=self.url_for(target, _external=True), parameters=params)
            signature_method = oauth.SignatureMethod_HMAC_SHA1()
            req.sign_request(signature_method, consumer, token)
            headers = req.to_header()

            method = getattr(self.app, method.lower())
            if req_type in ['query_string', 'post']:
                url = self.url_for(target, **req)
                rv = method(self.url_for(target, **req), **kwargs)
            elif req_type is 'header':
                url = self.url_for(target)
                rv = method(url, headers=headers, **kwargs)

            data = json.loads(rv.data)

            if not fail:
                assert data.get('status_code') == 1000, \
                    "Expected successful authentication, got: %s " % rv.data
                assert data.get('response_data').get('partner_id') == self.key.partner_id
                assert data.get('response_data').get('api_key_id') == self.key.id
            else:
                assert data.get('status_code') == 4303, \
                    "Expected unsuccessful authentication, got: %s " % rv.data
                assert not g.get('api_key')

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
