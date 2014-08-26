'''
Test our Flask-RESTful subclass
'''

from hoops.restful import Resource
from hoops.response import APIResponse
from hoops.exc import APIException
from hoops.status import library as status
from tests.api_tests import APITestBase
import hoops


class WordWordWord(Resource):
    def get(self):
        return APIResponse({'word': 'letter'})

    def put(self):
        raise status.API_FORBIDDEN

    def post(self):
        raise Exception("BANG")

    def delete(self):
        raise APIException(status.get('API_FORBIDDEN'))


class TestXMLList(Resource):
    def get(self):
        return APIResponse([{"test": 1}, {"test2": 2}])


class TestBasicResponse(Resource):
    def get(self):
        return "test"

    def post(self):
        return {"test": 1}


class TestRestFulApi(APITestBase):

    @classmethod
    def setup_app(cls):
        hoops.api.add_resource(WordWordWord, '/word', endpoint='word')
        hoops.api.add_resource(TestXMLList, '/list', endpoint='list')
        hoops.api.add_resource(TestBasicResponse, '/basic', endpoint='basic')
        super(TestRestFulApi, cls).setup_app()

    def test_app(self):
        data = self.validate(self.app.get('/word'), status.API_OK)
        assert data['response_data']['word'] == 'letter'

    def test_api_exc(self):
        self.validate(self.app.put('/word'), status.API_FORBIDDEN)
        #assert data['response_data']['word'] == 'letter'

    def test_api_exc_manual(self):
        self.validate(self.app.delete('/word'), status.API_FORBIDDEN)
        #assert data['response_data']['word'] == 'letter'

    def test_other_exc(self):
        '''Tests that tracebacks and exceptions are captured in DEBUG mode'''
        data = self.validate(self.app.post('/word'), status.API_UNHANDLED_EXCEPTION)
        assert 'exception' in data
        assert 'traceback' in data
        last_executed = data['traceback'][-1]
        assert 'test_restful.py' in last_executed[0]
        assert 'BANG' in last_executed[3]
        assert 'BANG' in data['exception']

    def test_other_exc_nodebug(self):
        '''Tests that tracebacks and exceptions are NOT included when DEBUG is false'''
        config = self._app.config.get('DEBUG')
        self._app.config['DEBUG'] = False
        data = self.validate(self.app.post('/word'), status.API_UNHANDLED_EXCEPTION)
        assert 'exception' not in data
        assert 'traceback' not in data
        self._app.config['DEBUG'] = config

    def test_encoding_detection(self):
        permutations = (
            ('application/xml', None, 'application/xml, application/json'),  # Undefined which is best
            ('text/xml', None, 'text/xml'),
            ('application/xml', 'xml', 'application/xml'),
            ('application/xml', 'xml', 'application/json'),
            ('application/xml', 'xml', 'text/xml'),
            ('application/json', 'json', 'application/xml'),
            ('application/json', 'json', 'application/json'),
            ('application/json', 'json', 'text/xml'),
            ('application/xml', None, 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('application/json', None, 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'),
            # Last entry is for browser simulation
        )

        def try_permutation(expected, output_format, accept, user_agent=None):
            headers = {}
            if accept:
                headers['Accept'] = accept
            if user_agent:
                headers['User-Agent'] = user_agent
            url = self.url_for('word', output_format=output_format)
            rv = self.app.get(url, headers=headers)
            assert rv.content_type == expected, "for url %s, got %s; expected %s; %s, %s, %s" % (
                url, rv.content_type, expected, output_format, accept, user_agent)

        for permutation in permutations:
            try_permutation(*permutation)

    def test_xml_serialize(self):
        rv = self.app.get(self.url_for('list', output_format="xml"))
        assert '<item><test>1</test></item><item><test2>2</test2></item>' in rv.data

    def test_basic_responses(self):
        data = self.validate(self.app.get(self.url_for('basic')), status.API_OK)
        assert data['response_data'] == 'test'
        data = self.validate(self.app.post(self.url_for('basic')), status.API_OK)
        assert data['response_data']['test'] == 1
