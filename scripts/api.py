import restkit
from restkit import Resource, RequestError
from restkit import OAuthFilter
import restkit.oauth2 as oauth
from flask import json
from BeautifulSoup import BeautifulStoneSoup
import sys

consumer_key = 'dev'
consumer_secret = 'XVgpEgeYld3lhjTu9ZXoxVkjku2TQFlfUbuxA4paU18'
token = 'hiMu97KpzlN2ttay3JI3Yhzq7aeYrILP3PLX7Pfg8j'
token_secret = 'gSaX071iHzijyqiVpKecgUxVyUgMBDH4TQYCeQLQTQE'

consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
token = oauth.Token(key=token, secret=token_secret)

app_url_base = 'http://127.0.0.1:5000'
verbose = False

class Results(object):
    test_results = []

    @classmethod
    def append(self, method, path, status, description=''):
        self.test_results.append([method, path, status, description])


class API(object):
    method = None

    def __call__(self, path, params=None, status_code=1000, http_status=200, validations=None, description=""):
        auth_filter = OAuthFilter('*', consumer, token)
        self.r = Resource(app_url_base + path, filters=[auth_filter])
        if params is None:
            params = {}

        self.print_req(path, params)

        body = None

        try:
            try:
                resp = self.request(params)
                body = resp.body_string()
            except restkit.errors.ResourceNotFound as r:
                resp = r.response
                body = r.msg

            print "Status: " + resp.status
            print "Content Type: " + resp.headers['Content-Type']

            sc = resp.status.split(' ')
            assert sc[0] == '{}'.format(http_status), 'Expected HTTP status %s, got %s' % (http_status, resp.status)

            if not status_code:
                print ""
                print "Test Result: OK"
                Results.append(self.method, path, 'OK', description)
                return ''

            reply = json.loads(body)
            assert '{}'.format(reply['status_code']) == '{}'.format(status_code), 'Expected API status %d, got %s' % (status_code, reply['status_code'])

            if validations:
                for validation in validations:
                    validation(reply)

            print ""
            Results.append(self.method, path, 'OK', description)
            print "Test Result: OK"

            if verbose:
                print "Response:"
                print body

            return reply['response_data']

        except Exception as e:
            Results.append(self.method, path, 'FAILED', description + ' %s' % type(e))
            print "Test Result:  FAILED"
            print "Exception: %s" % type(e)
            import traceback
            traceback.print_exc()

            print "Response:"
            print body

            typename = '%s' % type(e)
            if not isinstance(e, RequestError) and 'restkit.errors' in typename:  # Why the heck didn't these all derive from a base other than exceptions.Exception
                resp = e.response
                body = e.msg
                print "Status: " + resp.status
                print "Content Type: " + resp.headers['Content-Type']
                if 'text/html' in resp.headers['Content-Type']:
                    soup = BeautifulStoneSoup(body)
                    print "Title: " + soup.title.contents[0]
                else:
                    print body
            else:
                print e
            return None

    def print_req(self, path, params):
        print ""
        print "-------------------------------------------------------------------"
        print "%s %s" % (self.method, app_url_base + path)
        print ""
        if params:
            print "Params:"
            for key, value in params.iteritems():
                print "  %s = %s" % (key, value)
            print ""


class GET(API):
    method = 'GET'

    def request(self, params):
        return self.r.get(headers={'Accept': 'application/json'}, **params)


class POST(API):
    method = 'POST'

    def request(self, params):
        return self.r.post(headers={'Accept': 'application/json'}, payload=params)


class PUT(API):
    method = 'PUT'

    def request(self, params):
        return self.r.put(headers={'Accept': 'application/json'}, payload=params)


class DELETE(API):
    method = 'DELETE'

    def request(self, params):
        return self.r.delete(headers={'Accept': 'application/json'}, payload=params)
