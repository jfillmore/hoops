from flask import g
from formencode.validators import Int, OneOf, String
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound

from hoops.base import parameter, APIModelOperation
from hoops.response import APIResponse, PaginatedAPIResponse
from hoops.status import library as status_library
from hoops import db
import hoops

@parameter('limit', Int(min=1, max=100), "Page size", required=False, default=100)
@parameter('page', Int(min=0), "Page number", required=False, default=1)
@parameter('sort_by', String, "Sort field", required=False, default='id')
# TODO - restrict to sortable field list
@parameter('sort_order', OneOf(['asc', 'desc']), "Sort direction", required=False, default='asc')
# TODO - add cursor-style listing
class ListOperation(APIModelOperation):

    def process_request(self, *args, **kwargs):
        super(ListOperation, self).process_request(*args, **kwargs)
        try:
            # print self.get_base_query()
            pager = self.paginate_query(self.get_base_query())
        except NotFound:
            # 404 is raised when Flask-Alchemy's pagination finds no results with a page > 1
            raise status_library.exception('API_VALUE_TOO_HIGH', value='page')
        status = (status_library.API_NO_RECORDS_FOUND
                  if not pager.items
                  else status_library.API_OK)
        return PaginatedAPIResponse(
            pager.items,
            pagination=pager,
            params=self.params,
            status=status)

    def paginate_query(self, query):
        sort_field = getattr(self.model, self.params.get('sort_by', 'id'))
        sort_field_dir = getattr(sort_field, self.params.get('sort_order', 'asc'))
        sorted_query = query.order_by(sort_field_dir())
        result = sorted_query.paginate(self.params['page'], self.params['limit'])
        return result


class RetrieveOperation(APIModelOperation):

    def process_request(self, *args, **kwargs):
        super(RetrieveOperation, self).process_request(*args, **kwargs)
        return APIResponse(self.load_object())


class CreateOperation(APIModelOperation):

    def process_request(self, *args, **kwargs):
        super(CreateOperation, self).process_request(*args, **kwargs)

        obj = self.model(**self.params)
        if getattr(self.model, 'partner', None):
            obj.partner = g.partner

        db.session.add(obj)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise status_library.API_DUPLICATE_VALUE  # TODO verify that was the case
        return APIResponse(obj)


class NotSpecified(object):
    def __nonzero__(self):
        return False

    def __repr__(self):
        return "<unspecified>"

    def __str__(self):
        return "<unspecified>"


# class UpdateOperation(APIModelOperation):

#     def setup(self, *args, **kwargs):
#         self.object = self.load_object()
#         if not self.object.updates_permitted() and not getattr(self, 'force_update', False):
#             raise status_library.API_FORBIDDEN_UPDATE

#     def process_request(self, *args, **kwargs):
#         for param in self.params:
#             value = self.params.get(param, NotSpecified())
#             if not isinstance(value, NotSpecified):
#                 setattr(self.object, param, value)
#         db.session.add(self.object)
#         try:
#             db.session.commit()
#         except IntegrityError:
#             db.session.rollback()
#             # TODO verify that was the case
#             raise status_library.exception('API_DATABASE_UPDATE_FAILED',
#                                            resource=self.model.__tablename__)
#         return APIResponse(self.object)


# class include_related(parameter):

#     def __init__(self, field, column, validator, description, required=None, default=None):
#         super(include_related, self).__init__(field, validator, description)
#         self.column = column

#     def __call__(self, klass):
#         klass = super(include_related, self).__call__(klass)
#         if not hasattr(klass, 'related'):
#             related = {}
#         else:
#             related = copy.deepcopy(klass.related)
#         related[self.field] = self.column
#         klass.related = related

#         if hasattr(klass, 'orig_process_request'):
#             return klass

#         klass.orig_process_request = klass.process_request

#         def process_request(self, *args, **kwargs):
#             output = self.orig_process_request(*args, **kwargs)
#             to_include = [
#                 self.related[param]
#                 for param in filter(
#                     lambda param: self.combined_params.get(param, False),
#                     self.related.keys()
#                 )
#             ]
#             if not to_include:
#                 return output
#             data = output.response['response_data']
#             if isinstance(data, collections.Iterable):
#                 output.response['response_data'] = [
#                     item.to_json(include_subordinate=to_include)
#                     for item in data
#                 ]
#             else:
#                 output.response['response_data'] = data.to_json(include_subordinate=to_include)
#             return output

#         klass.process_request = process_request
#         return klass
