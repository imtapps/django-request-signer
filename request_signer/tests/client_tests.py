
from cStringIO import StringIO
import urllib2
import mock

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import unittest

from request_signer import constants
from request_signer.client.generic import Request, Response, Client

__all__ = ('ClientTests', )

class ClientTests(unittest.TestCase):

    def setUp(self):
        self.settings_name = 'SAMPLE_AUTH_DOMAIN'
        self.client_id_settings_name = 'SAMPLE_AUTH_CLIENT_ID'
        self.private_key_settings_name = 'SAMPLE_AUTH_PRIVATE_KEY'
        self.client = Client()
        self.domain = 'http://www.sample.com'
        self.path = '/some/path/'
        self.url = self.domain + self.path
        self.client_id = 'UJSDAYFH$%U&GCKDJBSG'
        self.private_key = 'Q0TBXqjE60nfoHaQ1CZxWxt4JBUyhBPJkH1y_274tDI='
        self.client_id_param_name = 'X-TEST-CLIENT-HEADER'
        self.signature_param_name = 'X-TEST-SIGNATURE'
        self.setup_client()

        self.endpoint = '/some/endpoint'
        self.urlopen_patch = mock.patch.object(urllib2, 'urlopen')
        self.urlopen = self.urlopen_patch.start()
        self.request = Request('GET', self.url, dict())

    def setup_client(self):
        setattr(self.client, 'domain_settings_name', self.settings_name)
        setattr(self.client, 'client_id_settings_name', self.client_id_settings_name)
        setattr(self.client, 'private_key_settings_name', self.private_key_settings_name)
        setattr(settings, self.settings_name, self.domain)
        setattr(settings, self.client_id_settings_name, self.client_id)
        setattr(settings, self.private_key_settings_name, self.private_key)

    def tearDown(self):
        self.urlopen_patch.stop()
        self.teardown_client()

    def teardown_client(self):
        source = settings
        self.safe_delattr(source, self.settings_name)
        self.safe_delattr(source, self.client_id_settings_name)
        self.safe_delattr(source, self.private_key_settings_name)

    def safe_delattr(self, source, name):
        try:
            delattr(source, name)
        except AttributeError:
            pass

    def get_response(self, http_method="GET", endpoint="/some/endpoint", *args, **kwargs):
        return self.client._get_response(http_method, endpoint, *args, **kwargs)

    def assert_client_raises_improperly_configured_with_attribute_name(self, client_attribute, client_property):
        delattr(self.client, client_attribute)
        with self.assertRaises(ImproperlyConfigured) as error:
            getattr(self.client, client_property)
        self.assertIn(client_attribute, error.exception.message)

    def assert_client_raises_improperty_configured_with_missing_settings_name(self, settings_name, client_property):
        delattr(settings, settings_name)
        with self.assertRaises(ImproperlyConfigured) as error:
            getattr(self.client, client_property)
        self.assertIn(settings_name, error.exception.message)

    @mock.patch('request_signer.client.generic.Request')
    def test_get_response_creates_request(self, request):
        method = 'GET'
        data = dict(this="is", some='data', right='here')
        with mock.patch.object(Client, '_get_service_url') as get_url:
            get_url.return_value = 'my_url'
            self.get_response(method, self.endpoint, data)

        request.assert_called_once_with(
            method,
            'my_url?{}={}&this=is&right=here&some=data&{}={}'.format(
                constants.CLIENT_ID_PARAM_NAME, self.client._client_id,
                constants.SIGNATURE_PARAM_NAME, 'KpgZbsM6iwzTkyDI4MHpZFVLDxcjd0A68-c3kcunBzg='),
            None,
        )

    @mock.patch('request_signer.client.generic.Request', mock.Mock())
    def test_get_response_gets_url_with_endpoint(self):
        with mock.patch.object(Client, '_get_service_url') as get_url:
            get_url.return_value = 'url'
            self.get_response(endpoint=self.endpoint)
        get_url.assert_called_once_with(self.endpoint)

    def test_get_url_returns_url_from_settings_with_endpoint(self):
        url = self.client._get_service_url(endpoint=self.endpoint)
        self.assertEqual(self.domain + self.endpoint, url)

    def test_raises_improperly_configured_when_no_domain_settings_in_settings(self):
        settings_name = self.settings_name
        client_property = '_base_url'
        self.assert_client_raises_improperty_configured_with_missing_settings_name(settings_name, client_property)

    def test_raises_improperly_configured_when_no_url_in_settings(self):
        settings_name = self.client_id_settings_name
        client_property = '_client_id'
        self.assert_client_raises_improperty_configured_with_missing_settings_name(settings_name, client_property)

    def test_raises_improperly_configured_when_no_private_key_in_settings(self):
        settings_name = self.private_key_settings_name
        client_property = '_private_key'
        self.assert_client_raises_improperty_configured_with_missing_settings_name(settings_name, client_property)

    def test_raises_improperly_configured_when_no_domain_settings_name(self):
        client_attribute = 'domain_settings_name'
        client_property = '_base_url'
        self.assert_client_raises_improperly_configured_with_attribute_name(client_attribute, client_property)

    def test_raises_improperly_configured_when_no_client_id_settings_name(self):
        client_attribute = 'client_id_settings_name'
        client_property = '_client_id'
        self.assert_client_raises_improperly_configured_with_attribute_name(client_attribute, client_property)

    def test_raises_improperly_configured_when_no_private_key_settings_name(self):
        client_attribute = 'private_key_settings_name'
        client_property = '_private_key'
        self.assert_client_raises_improperly_configured_with_attribute_name(client_attribute, client_property)

    def test_client_id_property_returns_client_id_from_settings(self):
        self.assertEqual(self.client_id, self.client._client_id)

    def test_private_key_property_returns_private_key_from_settings(self):
        self.assertEqual(self.private_key, self.client._private_key)

    @mock.patch('request_signer.client.generic.Request')
    def test_get_raw_response_invokes_urlopen_with_request(self, request):
        self.get_response()
        self.urlopen.assert_called_once_with(request.return_value)

    def test_returns_raw_response_wrapped_with_response_object_when_urllib_works_as_expected(self):
        raw_response = self.get_response()
        self.assertIsInstance(raw_response, Response)
        self.assertEqual(raw_response.raw_response, self.urlopen.return_value)

    def test_raw_error_returned_wrapped_with_response_object_when_exception_thrown(self):
        expected = urllib2.HTTPError(None, 500, None, None, StringIO())
        self.urlopen.side_effect = expected
        error_as_response = self.get_response()
        self.assertIsInstance(error_as_response, Response)
        self.assertEqual(expected, error_as_response.raw_response)
