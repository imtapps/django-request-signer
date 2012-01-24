import json
import urllib2

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.http import urlencode
from request_signer import constants, AuthSigner

__all__ = ('HttpMethodNotAllowed', 'Request', 'Response', 'Client', )

CLIENT_ERROR_MESSAGE = "Client implementations must define a `{0}` attribute"
CLIENT_SETTINGS_ERROR_MESSAGE = "Settings must contain a `{0}` attribute"

class Client(object):

    def _get_response(self, http_method, endpoint, data=None):
        try:
            response = urllib2.urlopen(self._get_request(http_method, endpoint, data))
        except urllib2.HTTPError as e:
            response = e
        return Response(response)

    def _get_request(self, http_method, endpoint, data=None):
        factory = SignedRequestFactory(http_method, self._client_id, self._private_key)
        return factory.create_request(self._get_service_url(endpoint), data)

    def _get_service_url(self, endpoint):
        return self._base_url + endpoint

    @property
    def _base_url(self):
        return self.get_setting('domain_settings_name')

    @property
    def _client_id(self):
        return self.get_setting('client_id_settings_name')

    @property
    def _private_key(self):
        return self.get_setting('private_key_settings_name')

    def get_setting(self, name):
        client_name = self.get_client_name(name)
        setting = getattr(settings, client_name, None)
        if not setting:
            raise ImproperlyConfigured(CLIENT_SETTINGS_ERROR_MESSAGE.format(client_name))
        return setting

    def get_client_name(self, name):
        client_name = getattr(self, name, None)
        if not client_name:
            raise ImproperlyConfigured(CLIENT_ERROR_MESSAGE.format(name))
        return client_name

class HttpMethodNotAllowed(Exception):
    pass

class SignedRequestFactory(object):

    def __init__(self, http_method, client_id, private_key):
        self.client_id = client_id
        self.private_key = private_key
        self.http_method = http_method

    def create_request(self, url, raw_data, *args, **kwargs):
        url = self.build_request_url(raw_data, url)
        data = self.get_data_payload(raw_data)
        return Request(self.http_method, url, data, *args, **kwargs)

    def build_request_url(self, raw_data, url):
        url = self.build_client_url(url)
        if self.is_get_request_with_data(raw_data):
            url += "&{0}".format(urlencode(raw_data))
        return self.build_signed_url(raw_data, url)

    def build_signed_url(self, raw_data, url):
        data = {} if self.is_get_request_with_data(raw_data) else raw_data
        signature = AuthSigner.get_signature(self.private_key, url, data)
        url += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, signature)
        return url

    def get_data_payload(self, raw_data):
        if raw_data and self.http_method.lower() != 'get':
            return urlencode(raw_data)

    def is_get_request_with_data(self, raw_data):
        return self.http_method.lower() == 'get' and raw_data

    def build_client_url(self, url):
        url += "?%s=%s" % (constants.CLIENT_ID_PARAM_NAME, self.client_id)
        return url

class Request(urllib2.Request, object):
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    def __init__(self, http_method, url, data, *args, **kwargs):
        method_lower = http_method.lower()
        if method_lower not in self.http_method_names:
            raise HttpMethodNotAllowed
        self.http_method = http_method
        super(Request, self).__init__(url, data, *args, **kwargs)

    def get_method(self):
        return self.http_method

class Response(object):

    def __init__(self, response):
        self.original_raw_response = None
        self.raw_response = response

    @property
    def status_code(self):
        return self.raw_response.code

    def read(self):
        if self.original_raw_response is None:
            self.original_raw_response = self.raw_response.read()
        return self.original_raw_response

    @property
    def json(self):
        response_content = self.read()
        if response_content == '':
            return {}
        return json.loads(response_content)

    @property
    def is_successful(self):
        return self._evaluate_response_code_for_success(self.status_code)

    def _evaluate_response_code_for_success(self, response_code):
        return response_code // 100 == 2