import copy
import re

from flask import g
from flask.ext.restful import abort
from formencode import Invalid, Schema
from formencode.validators import Validator

import hoops
from hoops.restful import Resource
from hoops.exc import APIValidationException
from hoops.status import library as status_library


class APIOperation(object):

    def __call__(self, *args, **kwargs):
        self.url_params = self.validate_url(**kwargs)
        self.params = self.validate_input()
        if hasattr(self, 'setup'):
            self.setup(*args, **kwargs)
        return self.process_request(*args, **kwargs)

    def __init__(self, resource=None, method='get'):
        self.resource = resource

    @property
    def combined_params(self):
        params = copy.deepcopy(getattr(self, 'params', {}))
        url_params = getattr(self, 'url_params', {})
        params.update(url_params)
        return params

    def _combine_schema(self, attr_name='schema'):
        resource_schema = getattr(self.resource, attr_name, None)
        operation_schema = getattr(self, attr_name, None)

        # Merge combined schemas, preferring the operation_schema settings and fields
        if resource_schema and operation_schema:
            schema = copy.deepcopy(operation_schema)
            for field in resource_schema.fields:
                if not field in schema.fields:
                    schema.add_field(field, resource_schema.fields[field])
        else:
            schema = resource_schema or operation_schema

        return schema or Schema()

    def validate_url(self, *args, **kwargs):
        schema = self._combine_schema('url_schema')
        if not schema:  # pragma: no cover
            return {}

        try:
            return schema.to_python(kwargs)
        except Invalid as e:
            if e.error_dict:
                failures = {field: e.error_dict[field].msg for field in e.error_dict}
            else:
                failures = {"unknown": e.msg}  # pragma: no cover
            raise APIValidationException(status_library.API_INPUT_VALIDATION_FAILED, failures)

    def validate_input(self):
        schema = self._combine_schema('schema')
        try:
            return schema.to_python(self.resource.get_parameters())
        except Invalid as e:
            if e.error_dict:
                failures = {field: e.error_dict[field].msg for field in e.error_dict}
            else:
                failures = {"unknown": e.msg}  # pragma: no cover
            raise APIValidationException(status_library.API_INPUT_VALIDATION_FAILED, failures)

    def process_request(self, *args, **kwargs):
        pass


class APIModelOperation(APIOperation):

    @property
    def model(self):
        return self.resource.model

    def get_base_query(self, limit_to_partner=True, **kwargs):
        '''Obtains the base query for a model-based operation.'''
        all_params = kwargs
        all_params.update(self.combined_params)
        query = self.resource.model.query
        return self.resource.get_base_query(**all_params)

    def load_object(self, **kwargs):
        item_id = self.combined_params.get(self.resource.object_id_param, None)
        id_column = getattr(self, 'id_column', 'id')
        column = getattr(self.model, id_column)
        item = self.get_base_query(**kwargs).filter(column == item_id).first()
        if item is None:
            raise status_library.exception('API_DATABASE_RESOURCE_NOT_FOUND', resource=self.resource.model.__tablename__)
        return item


class UnimplementedOperation(APIOperation):
    def __call__(self, *args, **kwargs):
        raise status_library.API_CODE_NOT_IMPLEMENTED


class APIResource(Resource):
    route = None
    model = None
    read_only = True
    object_id_param = None

    create = UnimplementedOperation()
    retrieve = UnimplementedOperation()
    update = UnimplementedOperation()
    remove = UnimplementedOperation()
    list = UnimplementedOperation()

    @classmethod
    def get_parameters(cls):

        def purge_oauth_keys(params):
            return {k: params[k] for k in filter(lambda item: not re.match(r'^oauth_', item), params)}

        from flask import request
        if request.method == 'GET':
            return purge_oauth_keys(request.args)
        else:
            return purge_oauth_keys(request.form)

    @classmethod
    def method(self, method):
        '''
        Decorator to bind a callable as the handler for a method.
        It sets the resource property on the callable to be the parent resource.
        '''
        def wrapper(cls, *args, **kwargs):
            cls.resource = self
            setattr(self, method, cls(resource=self))
            return cls
        return wrapper

    def get(self, **kwargs):
        if self.object_id_param in kwargs:
            return self.retrieve(**kwargs)
        return self.list(**kwargs)

    def post(self, **kwargs):
        if self.object_id_param in kwargs:
            abort(404)  # Can't POST with arguments in URL
        if self.read_only:
            abort(405)
        return self.create(**kwargs)

    def put(self, **kwargs):
        if not self.object_id_param in kwargs:
            abort(404)  # Can't PUT without arguments (that may have an ID)
        if self.read_only:
            abort(405)
        return self.update(**kwargs)

    def delete(self, **kwargs):
        if not self.object_id_param in kwargs:
            abort(404)  # Can't DELETE without arguments (that may have an ID)
        if self.read_only:
            abort(405)
        return self.remove(**kwargs)

    @classmethod
    def register(cls):
        routes = [cls.route]
        object_route = getattr(cls, 'object_route', None)
        if object_route:
            routes.append(object_route)
        hoops.api.add_resource(cls, *routes)


class base_parameter(object):
    schema_property = 'schema'

    def __init__(self, field, validator, description):
        self.field = field
        if isinstance(validator, Validator):
            self.validator = validator
        else:
            self.validator = validator()
        self.validator.__doc__ = description

    def __call__(self, klass):
        if not hasattr(klass, self.schema_property):
            schema = Schema()
        else:
            schema = copy.deepcopy(getattr(klass, self.schema_property))
        schema.add_field(self.field, self.validator)
        setattr(klass, self.schema_property, schema)

        return klass


class parameter(base_parameter):
    '''Binds a formencode validator to the schema in either a APIResource or APIOperation.
    If the Schema is not yet present, one is created.

    The ``required`` and ``default`` named parameters can be used as shortcuts to modify the
    ``validator`` as if_missing=default and not_empty=required.

    Example:
    @parameter("id", validator=formencode.validators.Int(), description="Unique ID of object", required=True, default=None)
    '''
    def __init__(self, field, validator, description, required=None, default=None):
        super(parameter, self).__init__(field, validator, description)
        if required is not None:
            self.validator.not_empty = required
        if default is not None:
            self.validator.if_missing = default


class url_parameter(base_parameter):
    '''Binds a formencode validator to the url_schema in either a APIResource or APIOperation.
    If the URL Schema is not yet present, one is created.

    All validators added to the schema this way have not_empty=True (as they are mandatory).

    Example:
    @url_parameter("id", validator=formencode.validators.Int(), description="Unique ID of object")
    '''

    schema_property = 'url_schema'