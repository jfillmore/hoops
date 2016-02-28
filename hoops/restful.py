from functools import wraps
import json
import sys
import traceback
from copy import deepcopy
from flask.ext import restful
from flask import make_response, request, Markup, g, current_app
from werkzeug.exceptions import HTTPException

from hoops.status import library as status_library
from hoops.response import APIResponse
from hoops.exc import APIException, APIValidationException
from hoops.status import APIStatus
from hoops.utils import Struct
import logging

error_map = {
    200: status_library.API_OK,
    403: status_library.API_FORBIDDEN,
    404: status_library.API_RESOURCE_NOT_FOUND,
    405: status_library.API_INVALID_REQUEST_METHOD,
    500: status_library.API_UNHANDLED_EXCEPTION,
    501: status_library.API_CODE_NOT_IMPLEMENTED,
}

api_logger = logging.getLogger('api.info')
request_logger = logging.getLogger('api.request')
api_error_logger = logging.getLogger('api.error')
error_logger = logging.getLogger('error')


class Resource(restful.Resource):
    # applies to all inherited resources; OauthAPI will append 'require_oauth' on init
    method_decorators = []


class API(restful.Api):
    def __init__(self, *args, **kwargs):
        super(API, self).__init__(*args, **kwargs)
        self.representations = {
            #'application/xml': output_xml,
            #'text/xml': output_xml,
            'application/json': output_json,
        }

    def make_response(self, *args, **kwargs):
        response = restful.Api.make_response(self, *args, **kwargs)
        try:
            message = getattr(args[0], 'response', None).get('status_message', None)
        except:
            message = args[0]
        request_logger.info('%s: %s', response.data, message)
        if response.status_code >= 500:
            error_logger.exception('%s: %s', response.data, message)
        return response

    def handle_error(self, e):
        if isinstance(e, HTTPException):
            return self.make_response(
                APIResponse(None, status=error_map.get(e.code, APIStatus(http_status=e.code, status_code=e.code * 10, message=e.description))),
                e.code)
        elif isinstance(e, APIValidationException):
            return self.make_response(
                APIResponse(None, status=e.status, extra=e.extra),
                e.status.http_status)
        elif isinstance(e, APIException):
            return self.make_response(
                APIResponse(None, status=e.status),
                e.status.http_status)
        status = status_library.API_UNHANDLED_EXCEPTION
        if current_app.config.get('DEBUG'):
            tb_info = sys.exc_info()
            return self.make_response(
                APIResponse(None, status=status, extra={
                    'exception': traceback.format_exception_only(tb_info[0], tb_info[1])[0],
                    'traceback': traceback.extract_tb(tb_info[2])
                }), status.http_status)
        # We don't use the default error handler
        # e.g.: return super(API, self).handle_error(e)
        return self.make_response(
            APIResponse(None, status=status), status.http_status)

    def _should_use_fr_error_handler(self):
        """ Determine if error should be handled with FR or default Flask
            Return True since we need all errors handled in above handler.
        """
        return True

    def mediatypes(self):
        """Replaces the acceptable media types with application/json if the request came from a browser.
        Also looks for output_type parameter.
        """
        if request.args.get('output_format', '') == 'xml' or request.form.get('output_format', '') == 'xml':
            return ['application/xml']
        elif request.args.get('output_format', '') == 'json' or request.form.get('output_format', '') == 'json':
            return ['application/json']

        if (('text/html' in request.accept_mimetypes or
             'application/xhtml+xml' in request.accept_mimetypes)
                and 'Mozilla' in request.user_agent.string):
            return ['application/json']
        return super(API, self).mediatypes()

    def register(self, cls):
        routes = [cls.route] if cls.route else []
        object_route = getattr(cls, 'object_route', None)
        if object_route:
            routes.append(object_route)
        if routes:
            [api_logger.debug('Adding route %s' % route) for route in routes]
            self.add_resource(cls, *routes, endpoint=cls.route)


class OAuthAPI(API):
    '''Only a single API at a time can be supported. Using OAuthAPI causes all resources to require OAuth.'''

    def __init__(self, *args, **kwargs):
        # TODO:
        # - make oauth app specific (e.g. extra params, diff Resource for Oauth inheritence, etc?)
        # - allow adhok usage of oauth on some Resource objects
        # - define alternate oauth arg handling methods besides static creds
        oauth_args = kwargs['oauth_args']
        del(kwargs['oauth_args'])
        super(API, self).__init__(*args, **kwargs)
        Resource.method_decorators = [require_oauth]
        Resource.oauth_args = Struct(**oauth_args)


def require_oauth(func):
    '''Auth wrapper from http://flask-restful.readthedocs.org/en/latest/extending.html?highlight=authentication'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        from hoops.oauth_provider import oauth_authentication
        # TODO: read server_oauth_creds from args/func
        server_oauth_creds = {}
        oauth_creds = oauth_authentication(server_oauth_creds)
        if not oauth_creds:
            # This is highly unlikely to occur, as oauth raises exceptions on problems
            restful.abort(401)  # pragma: no cover
        return func(*args, **kwargs)
    return wrapper


def prepare_output(data, code, headers=None):
    if not isinstance(data, APIResponse):
        data = APIResponse(data, status=error_map.get(code, APIStatus(
            http_status=code, status_code=code * 10, message=data
        )))

    out = data.to_json()
    code = data.status.http_status

    return_string = unicode(data.response)
    response_data = unicode(data.response.get('response_data')) if data.response.get('response_data') else return_string

    request_logger.info('Response %d chars: %s...', len(return_string), unicode(response_data[:50]))
    request_logger.debug('Response body: %s', return_string)

    return out, code


def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""
    out, code = prepare_output(data, code, headers)
    resp = make_response(json.dumps(out,
                                    sort_keys=True,
                                    indent=4,
                                    separators=(',', ': ')), code)
    resp.headers.extend(headers or {})
    return resp


#def output_xml(data, code, headers=None):
#    """Makes a Flask response with a XML encoded body"""
#    out, code = prepare_output(data, code, headers)
#    resp = xmlify(out)
#    resp.code = code
#    resp.headers.extend(headers or {})
#
#    return resp
#
#
#def xmlify(output):
#    """
#    xmlfy takes a dictionary and converts it to xml.
#    """
#    XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'
#    nodes = serialize_xml({'jetlaunch': output})
#
#    r = make_response(Markup(XML_DECLARATION + ''.join(etree.tostring(node) for node in nodes)))
#    r.mimetype = 'text/xml'
#
#    return r
#
#
#def serialize_xml(root):
#    node = None
#    node_stack = []
#    for key in root.keys():
#        node = etree.Element(key)
#        if isinstance(root[key], dict):
#            inner_node_stack = serialize(root[key])
#            for inner_node in inner_node_stack:
#                node.append(inner_node)
#        elif isinstance(root[key], list):
#            for item in root[key]:
#                itemnode = etree.Element('item')   # magic string
#                inner_node_stack = serialize(item)
#                for inner_node in inner_node_stack:
#                    itemnode.append(inner_node)
#                node.append(itemnode)
#        else:
#            if root[key] is not None:
#                node.text = unicode(root[key])
#        node_stack.append(node)
#
#    return node_stack
