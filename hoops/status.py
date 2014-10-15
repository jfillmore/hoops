
from flask.ext.babel import gettext

from hoops.exc import APIException


class MissingParameterError(KeyError):
    pass


class APIStatus(object):
    '''Describes an API status code, along with it's HTTP status code, and a descriptive status message'''

    http_status = 200  # OK
    status_code = 1000  # OK
    _message = "Unset"

    def __init__(self, http_status, status_code, message, *args, **kwargs):
        '''Set up an API status message with optional (positional, named) arguments, performing gettext on the message'''
        self.http_status = http_status
        self.status_code = status_code
        try:
            self.set_message(message, *args, **kwargs)
        except KeyError as e:
            raise MissingParameterError("Message '%s' missing argument '%s'" % (message, e))

    def __repr__(self):
        return "<%d - %d %s>" % (self.http_status, self.status_code, self.message)

    @property
    def message(self):
        '''Read-only property for the gettext processed message'''
        return self._message

    def set_message(self, message, *args, **kwargs):
        '''Sets the message property of a status message, performing gettext (with substitution if needed)'''
        if kwargs:
            self._message = gettext(message, *args, **kwargs)
        else:
            self._message = gettext(message)
        return self._message

    def get_dict(self):
        '''Returns a dict suitable for merging into an API response'''
        return {
            "status_code": self.status_code,
            "status_message": self.message,
        }


class StatusLibrary(object):
    '''This class is a factory for obtaining APIStatus objects appropriately initialized for a given API Status constant'''

    def __getattr__(self, name):
        '''Gets one API status message (without arguments)'''
        item = self.get(name)
        if item.status_code >= 2000:
            return APIException(item)
        return item

    def get(self, name, **kwargs):
        '''Gets one API status message with optional arguments for those messages that have positional parameters'''
        status = self.__library.get(name, None)
        if not status:
            raise KeyError("Status Message %s not found" % name)
        kwargs.update(dict(zip(('http_status', 'status_code', 'message'), status)))
        return APIStatus(**kwargs)

    def exception(self, name, **kwargs):
        status = self.get(name, **kwargs)
        return APIException(status)

    __library = {
        # 2xxx
        'API_OK': (200, 1000, u'Ok'),
        'API_NO_RECORDS_FOUND': (200, 1004, u'No records found'),

        # 4xxx - Input errors (mostly validation errors)
        'API_BAD_REQUEST': (400, 4000, u'The API request can\'t be fulfilled due to bad syntax in URL'),
        'API_UNAUTHORIZED_ACCESS': (401, 4001, u'The API request has not been authenticated'),
        'API_FORBIDDEN': (403, 4003, u'The API request is not allowed.'),
        'API_RESOURCE_NOT_FOUND': (404, 4004, u'Couldn\'t find the requested resource'),
        'API_INVALID_REQUEST_METHOD': (405, 4005, u'Method not supported'),
        'API_CONTENT_NOT_ACCEPTED': (406, 4006, u'The API request can\'t be fulfilled due to unsupported response content'),
        'API_REQUEST_TIMED_OUT': (408, 4008, u'A timeout occurred while trying to fulfil the requested API'),
        'API_CONFLICT_IN_REQUEST': (409, 4009, u'The API request can\'t be fulfilled due to a conflict with current state'),
        'API_REQUEST_URL_NO_LONGER_AVAILABLE': (410, 4010, u'The API request url is no longer served'),
        'API_CONTENT_LENGTH_MISSING': (411, 4011, u'The API request can\'t be fulfilled due to missing content length in header'),
        'API_PRECONDITION_FAILED': (412, 4012, u'The API request can\'t be fulfilled due to failed preconditions in header'),
        'API_REQUEST_ENTITY_TOO_LARGE': (413, 4013, u'The API request can\'t be fulfilled due to oversized request entity'),
        'API_INPUT_VALIDATION_FAILED': (400, 4100, u'Input validation error'),
        'API_MISSING_PARAMETER': (400, 4101, u"Missing parameter '%(parameter)s'"),
        'API_EMPTY_VALUE_PROVIDED': (400, 4102, u'Value can\'t be empty'),
        'API_VALUE_TOO_SHORT': (400, 4103, u'Value is too short'),
        'API_VALUE_TOO_LONG': (400, 4104, u'Value is too long'),
        'API_VALUE_TOO_SMALL': (400, 4105, u'Value is too small'),
        'API_VALUE_TOO_BIG': (400, 4106, u'Value is too big'),
        'API_INVALID_DATA_TYPE': (400, 4110, u'Invalid data type for value'),
        'API_STRING_VALUE_REQUIRED': (400, 4111, u'String value is needed'),
        'API_INTEGER_VALUE_REQUIRED': (400, 4112, u'Integer value is needed'),
        'API_REAL_NUMBER_VALUE_REQUIRED': (400, 4113, u'Real Number value is needed'),
        'API_BOOLEAN_VALUE_REQUIRED': (400, 4114, u'Boolean value is needed'),
        'API_UNICODE_VALUE_REQUIRED': (400, 4115, u'Unicode value is needed'),
        'API_INVALID_DATA_FORMAT': (400, 4120, u'Invalid input data format'),
        'API_INVALID_CHARACTER_FOUND': (400, 4121, u'Invalid characters in value'),
        'API_DUPLICATE_VALUE': (400, 4191, u'Value already exists'),
        'API_INVALID_INPUT_METHOD': (400, 4195, u'The API request can\'t be fulfilled due to invalid HTTP method'),
        'API_INVALID_CONTENT_HEADER': (400, 4196, u'Invalid content headers (Content type doesn\'t match with data)'),
        'API_MIXED_REQUEST_CONTENT_TYPE': (400, 4197, u'Mixing of request content type'),
        'API_VALUE_TOO_HIGH': (400, 4107, u'%(value)s too high'),
        'API_VALUE_TOO_LOW': (400, 4108, u'%(value)s too low'),
        'API_INVALID_VALUE': (400, 4109, u'Invalid value \'%(value)s\''),
        'API_DONOT_ACCEPT_PARAM': (400, 4116, u'%(key)s can\'t be specified in parameter list.'),
        'API_UNEXPECTED_INPUT_PARAMETER': (400, 4117, u'%(key)s can\'t be updated in %(model)s model'),

        #42xx
        'API_DATABASE_RESOURCE_NOT_FOUND': (404, 4204, u"Requested %(resource)s not found"),
        'API_FORBIDDEN_ACCESS': (401, 4203, u'Forbidden - The %(child_resource)s belongs to another %(parent_resource)s'),
        'API_FORBIDDEN_DELETE': (401, 4205, u'Cannot delete a %(parent_resource)s with active users or services'),
        'API_FORBIDDEN_UPDATE': (401, 4206, u'Update not permitted'),
        'API_DATABASE_UPDATE_FAILED': (400, 4220, u'Requested %(resource)s could not be updated with the given parameters'),
        'API_DATABASE_DELETE_FAILED': (400, 4221, u'Requested %(resource)s could not be deleted'),

        # 43xx
        'API_AUTHENTICATION_ERROR': (401, 4300, u'Authentication error'),
        'API_EXPIRED_TIMESTAMP': (401, 4301, u'Expired timestamp'),
        'API_UNEXPECTED_OAUTH_SIGNATURE_METHOD': (401, 4302, u'Unexpected Oauth signature method'),
        'API_INVALID_OAUTH_SIGNATURE': (401, 4303, u'Invalid oauth signature'),
        'API_UNKNOWN_OAUTH_CONSUMER_KEY': (401, 4304, u'Unknown consumer key'),
        'API_AUTHENTICATION_REQUIRED': (401, 4305, u'Authentication Required'),

        # 5xxx
        'API_UNHANDLED_EXCEPTION': (500, 5000, u'An internal server error occurred'),
        'API_DATABASE_OPERATION_FAILED': (500, 5203, u'Database operation failed'),
        'EXTERNAL_API_EXCEPTION': (500, 5100, u'Request to external API caused an exception with status code - {resource}'),
        'API_CODE_NOT_IMPLEMENTED': (501, 5001, u'Code not implemented'),
        'API_ULTIMATE_QUESTION': (404, 4999, u'The Answer to the Ultimate Question of Life, the Universe, and Everything')
    }


library = StatusLibrary()
