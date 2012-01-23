import json
import urllib2

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.http import urlencode

import request_signer

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
        request = Request(http_method, self._get_service_url(endpoint), data)
        self._sign_request(request)
        return request

    def _sign_request(self, request):
        signer = request_signer.AuthSigner(self._private_key)
        signature = signer.create_signature(request.get_selector(), request.get_data_dict())
        request.add_header(self._signature_param_name, signature)
        request.add_header(self._client_id_param_name, self._client_id)

    def _get_service_url(self, endpoint):
        return self._base_url + endpoint

    @property
    def _signature_param_name(self):
        return self.get_client_name('signature_param_name')

    @property
    def _client_id_param_name(self):
        return self.get_client_name('client_id_param_name')

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

class Request(urllib2.Request, object):
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    def get_data_dict(self):
        return self._data_dict

    def __init__(self, http_method, url, data, *args, **kwargs):
        self._data_dict = None
        method_lower = http_method.lower()
        if method_lower not in self.http_method_names:
            raise HttpMethodNotAllowed
        self.http_method = http_method

        if method_lower == 'get' and data:
            url += "?{0}".format(urlencode(data))
            data = None
        elif data:
            self._data_dict = data
            data = urlencode(data)

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