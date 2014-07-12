import sys
import os
# note we need the parent directory of this script
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from formencode.validators import StringBool, UnicodeString, Int, OneOf

from hoops.restful import Resource, APIResource
from hoops.base import APIOperation, parameter, url_parameter


class ExampleGet(APIOperation):
    def process_request(self, **kwargs):
        return {
            'example': 'GET works',
            'kwargs': kwargs
        }


class ExamplePost(APIOperation):
    def process_request(self, **kwargs):
        return {
            'example': 'POST works',
            'kwargs': kwargs
        }


class ExamplePut(APIOperation):
    def process_request(self, **kwargs):
        return {
            'example': 'PUT works',
            'kwargs': kwargs
        }


class ExampleDelete(APIOperation):
    def process_request(self, **kwargs):
        return {
            'example': 'DELETE works',
            'kwargs': kwargs
        }


class FooGet(APIOperation):
    def process_request(self, **kwargs):
        return {
            'foo': 'get thee to the bar',
            'kwargs': kwargs
        }


@parameter('foo', UnicodeString(max=3, if_missing='get thee to the next whiskey bar'), 'Foo is whatever you want it to be -- up to 3 characters long')
class FooPost(APIOperation):
    def process_request(self, **kwargs):
        return {
            'foo': kwargs['foo'],
            'kwargs': kwargs
        }


@parameter('foo', Int(max=42), 'Foo must be an int less than or equal to 42')
class FooPut(APIOperation):
    def process_request(self, **kwargs):
        return {
            'foo': 'get thee to the bar',
            'kwargs': kwargs
        }


@parameter('foo', OneOf([2, 4, 6, 8, 10]), 'Foo must an even number between 1 and 10 inclusive')
class FooDelete(APIOperation):
    def process_request(self, **kwargs):
        return {
            'foo': 'bye, bye miss american pie',
            'kwargs': kwargs
        }


class Example(APIResource):
    route = '/'
    get = ExampleGet()
    post = ExamplePost()
    put = ExamplePut()
    delete = ExampleDelete()


class Foo(APIResource):
    route = '/foo'
    get = FooGet()
    post = FooPost()
    put = FooPut()
    delete = FooDelete()


class Bar(APIResource):
    route = '/bar'

    def get(self, **kwargs):
        return kwargs


