
from flask import request
from oauth import OAuthRequest, OAuthError, OAuthMissingParameterError
from oauth.signature_method.hmac_sha1 import OAuthSignatureMethod_HMAC_SHA1

from hoops.status import library as status
# FIXME: partner_api_key from PartnerAPIKey
# from models.core import PartnerAPIKey


# TODO: support a mechanism for specifying how the oauth keys will be loaded
# e.g.
#   1. User passes in the keys to authorize against
#   2. User passes in functions to invoke to get keys
#   3. User passes in a table/model with a specific schema

OAUTH_PARAMS = (
    'oauth_consumer_key',
    'oauth_consumer_secret',
    'oauth_consumer_secret',
    'oauth_token',
    'oauth_token_secret',
    'oauth_body_hash',
    'oauth_timestamp',
    'oauth_signature',
    'oauth_signature_method',
    'oauth_nonce',
    'oauth_version',
)


def oauth_authentication():
    params = {key: value for key, value in request.values.iteritems()}
    oauth_request = OAuthRequest(url=request.base_url, http_method=request.method, params=params, headers=request.headers)

    if not oauth_request.params.get('oauth_consumer_key'):
        raise status.API_AUTHENTICATION_REQUIRED

    # FIXME: partner_api_key from PartnerAPIKey
    # partner_api_key = .query_active.filter_by(
    #     consumer_key=oauth_request.params.get('oauth_consumer_key')).first()
    partner_api_key = 'WRONG_KEY'
    if not partner_api_key or not partner_api_key.partner.enabled:
        raise status.API_UNKNOWN_OAUTH_CONSUMER_KEY

    consumer = {
        'oauth_consumer_key': partner_api_key.consumer_key,
        'oauth_consumer_secret': partner_api_key.consumer_secret
    }
    token = {
        'oauth_token': partner_api_key.token,
        'oauth_token_secret': partner_api_key.token_secret
    }

    try:
        oauth_request.validate_signature(
            OAuthSignatureMethod_HMAC_SHA1, consumer, token)

        return partner_api_key

    except OAuthMissingParameterError as e:
        raise status.exception('API_MISSING_PARAMETER', parameter=e.parameter_name)
    except OAuthError as e:
        if 'Expired timestamp' in e.message:
            raise status.API_EXPIRED_TIMESTAMP
        elif 'Unexpected oauth_signature_method.' in e.message:
            raise status.API_UNEXPECTED_OAUTH_SIGNATURE_METHOD
        elif e.message == 'Invalid Signature':
            raise status.API_INVALID_OAUTH_SIGNATURE
        else:
            raise  # pragma: no cover
