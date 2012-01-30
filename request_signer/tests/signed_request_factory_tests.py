
from urllib import urlencode
import mock

from django.utils import unittest

from request_signer.client import generic
from request_signer import constants

__all__ = ('SignedRequestFactoryTests', )

class SignedRequestFactoryTests(unittest.TestCase):

    def setUp(self):
        self.client_id = 'client_id'
        self.private_key = 'oVB_b3qrP3R6IDApALqehQzFy3DpMfob6Y4627WEK5A='
        self.factory = generic.SignedRequestFactory('GET', self.client_id, self.private_key)

    def test_sets_client_id_in_init(self):
        self.assertEqual(self.client_id, self.factory.client_id)

    def test_sets_private_key_in_init(self):
        self.assertEqual(self.private_key, self.factory.private_key)

    def test_adds_client_id_to_url(self):
        url = 'http://example.com/my/url'
        request = self.factory.create_request(url, {})

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    def test_adds_signature_to_url(self):
        url = 'http://example.com/my/url'
        request = self.factory.create_request(url, {})

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    @mock.patch('urllib2.Request.__init__')
    def test_urlencodes_data_as_part_of_url_when_method_is_get(self, urllib2_request):
        self.factory.create_request('www.myurl.com', {'some':'da ta', 'goes':'he re'})
        self.assertEqual(None, urllib2_request.call_args[0][1])
        url = "www.myurl.com?{}={}&some=da+ta&goes=he+re&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            '6dBfb4JhoJIm7FyzktbhFxBFyLBPTmXn-MLkV-RXLng='
        )
        self.assertEqual(url, urllib2_request.call_args[0][0])

    @mock.patch('urllib2.Request.__init__')
    def test_passes_data_to_urllib_request_when_method_is_not_get(self, urllib2_request):
        data = {'some': 'da ta', 'goes': 'he re'}
        self.factory.http_method = 'POST'
        self.factory.create_request('www.myurl.com', data)
        self.assertEqual(urlencode(data), urllib2_request.call_args[0][1])
        url = "www.myurl.com?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            self.client_id,
            constants.SIGNATURE_PARAM_NAME,
            '3sh6DOlYgbsCGT5rNlY819eFAdfl6Fy9GiyHHgUAwLQ='
        )
        self.assertEqual(url, urllib2_request.call_args[0][0])

    def test_payload_is_empty_on_get_request_when_signed(self):
        url = "www.myurl.com?asdf=1234"
        data = {'asdf': '1234'}

        first_request = self.factory._build_signed_url(url, data)
        second_request = self.factory._build_signed_url(url, {})

        self.assertEqual(first_request, second_request)
