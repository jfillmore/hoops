
from flask import request
from oauth import OAuthRequest, OAuthError, OAuthMissingParameterError
from oauth.signature_method.hmac_sha1 import OAuthSignatureMethod_HMAC_SHA1

from hoops.status import library as status


# TODO: support a mechanism for specifying how the oauth keys will be loaded
# e.g.
#   1. User passes in the keys to authorize against - Done
#   2. User passes in functions to invoke to get keys - Done
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


def oauth_authentication(oauth_creds=None):
    params = {key: value for key, value in request.values.iteritems()}
    if request.method == 'GET':
        oauth_request = OAuthRequest(url=request.base_url, http_method=request.method, params=params, headers=request.headers)
    else:
        oauth_request = OAuthRequest(url=request.base_url, http_method=request.method, headers=request.headers)
    if not oauth_request.params.get('oauth_consumer_key'):
        raise status.API_AUTHENTICATION_REQUIRED
    if not oauth_creds:
        raise status.API_UNKNOWN_OAUTH_CONSUMER_KEY
    if hasattr(oauth_creds, '__call__'):
        # we may have been given a function to call to get the creds each time
        oauth_creds = oauth_creds(request, oauth_request)
    consumer = {
        'oauth_consumer_key': oauth_creds.consumer_key,
        'oauth_consumer_secret': oauth_creds.consumer_secret
    }
    token = {
        'oauth_token': oauth_creds.token,
        'oauth_token_secret': oauth_creds.token_secret
    }

    try:
        oauth_request.validate_signature(OAuthSignatureMethod_HMAC_SHA1, consumer, token)
        return oauth_creds
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
