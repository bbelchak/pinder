import urlparse
import httplib2
try:
    import json
except ImportError:
    import simplejson as json

from pinder.exc import HTTPUnauthorizedException, HTTPNotFoundException


class HTTPConnector(object):
    """Makes the actual connection to the server and handles the response"""
    def __init__(self, subdomain, token, ssl=False, ua=''):
        # The User agent of the client
        self.user_agent = ua
        schema = ('http', 'https')[ssl==True]
        # The URI object of the Campfire account.
        self.uri = urlparse.urlparse(
            "%s://%s.campfirenow.com" % (schema, subdomain))
        self._http = httplib2.Http(timeout=5)
        self._http.force_exception_to_status_code = True
        self._http.add_credentials(token, 'X')

    def get(self, path='', data=None, headers=None):
        return self._request('GET', path, data, headers)

    def post(self, path, data=None, headers=None):
        return self._request('POST', path, data, headers)

    def put(self, path, data=None, headers=None):
        return self._request('PUT', path, data, headers)

    def _uri_for(self, path=''):
        return "%s/%s.json" % (urlparse.urlunparse(self.uri), path)

    def _request(self, method, path, data=None, additional_headers=None):
        additional_headers = additional_headers or dict()
        data = json.dumps(data or dict())

        headers = {}
        headers['user-agent'] = self.user_agent
        headers['content-type'] = 'application/json'
        headers['content-length'] = str(len(data))
        headers.update(additional_headers)

        if method in ('GET', 'POST', 'PUT', 'DELETE'):
            location = self._uri_for(path)
        else:
            raise Exception('Unsupported HTTP method: %s' % method)

        response, body = self._http.request(location, method, data, headers)

        if response.status == 401:
            raise HTTPUnauthorizedException(
                "You are not authorized to access the resource: '%s'" % path)
        elif response.status == 404:
            raise HTTPNotFoundException(
                "The resource you are looking for does not exist (%s)" % path)

        try:
            return json.loads(body)
        except ValueError, e:
            if response.status != 200:
                raise Exception("Something did not work fine: %s - %s" % (
                    str(e), body))
