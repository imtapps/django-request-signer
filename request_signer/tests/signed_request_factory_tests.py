
import mock
from urllib import urlencode

from django import test

from request_signer.client import generic
from request_signer import constants

__all__ = ('SignedRequestFactoryTests', )

class SignedRequestFactoryTests(test.TestCase):

    def setUp(self):
        self.client_id = 'client_id'
        self.private_key = 'oVB_b3qrP3R6IDApALqehQzFy3DpMfob6Y4627WEK5A='
        self.sut = generic.SignedRequestFactory('GET', self.client_id, self.private_key)

    def test_sets_client_id_in_init(self):
        self.assertEqual(self.client_id, self.sut.client_id)

    def test_sets_private_key_in_init(self):
        self.assertEqual(self.private_key, self.sut.private_key)

    def test_adds_client_id_to_url(self):
        url = 'http://example.com/my/url'
        request = self.sut.create_request(url, {})

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    def test_adds_signature_to_url(self):
        url = 'http://example.com/my/url'
        request = self.sut.create_request(url, {})

        querystring = "?{}={}".format(constants.CLIENT_ID_PARAM_NAME, self.client_id)
        querystring += "&{}={}".format(constants.SIGNATURE_PARAM_NAME, 'N1WOdyaBUVlPjKVyL3ionapOLAasFdvagfotfCdCW-Y=')
        self.assertEqual(url + querystring, request.get_full_url())

    @mock.patch('urllib2.Request.__init__')
    def test_urlencodes_data_as_part_of_url_when_method_is_get(self, urllib2_request):
        self.sut.create_request('www.myurl.com', {'some':'da ta', 'goes':'he re'})
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
        self.sut.http_method = 'POST'
        self.sut.create_request('www.myurl.com', data)
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

        first_request = self.sut._build_signed_url(url, data)
        second_request = self.sut._build_signed_url(url, {})

        self.assertEqual(first_request, second_request)

    def test_get_data_payload_returns_none_when_no_raw_data(self):
        payload_data = self.sut._get_data_payload(None, {})
        self.assertEqual(None, payload_data)

    def test_get_data_payload_returns_none_when_get_request(self):
        self.sut.http_method = "GET"
        payload_data = self.sut._get_data_payload({"some": "data"}, {})
        self.assertEqual(None, payload_data)

    def test_get_data_payload_returns_properly_encoded_data_when_content_type_header_present(self):
        encoder = mock.MagicMock()
        self.sut.http_method = "POST"
        self.sut.content_type_encodings = {"application/json": encoder}

        data = {"some": "data"}
        request_headers = {"Content-Type": "application/json"}
        payload_data = self.sut._get_data_payload(data, request_headers)
        self.assertEqual(encoder.return_value, payload_data)
        encoder.assert_called_once_with(data)

    def test_get_data_payload_returns_default_encoded_data_when_no_content_type_header(self):
        self.sut.http_method = "POST"

        data = {"some": "data"}
        with mock.patch("request_signer.client.generic.base.default_encoding") as encoder:
            payload_data = self.sut._get_data_payload(data, {})
        self.assertEqual(encoder.return_value, payload_data)
        encoder.assert_called_once_with(data)

    def test_create_request_sends_header_data_to_get_data_payload(self):
        raw_data = {"my": "data"}
        request_kwargs = {"headers": {"Content-Type": "application/json"}}
        with mock.patch.object(self.sut, "_get_data_payload") as get_payload:
            self.sut.create_request("/", raw_data, **request_kwargs)
        get_payload.assert_called_once_with(raw_data, request_kwargs["headers"])

    def test_create_request_sends_empty_dict_to_get_data_payload_when_no_header(self):
        raw_data = {"my": "data"}
        with mock.patch.object(self.sut, "_get_data_payload") as get_payload:
            self.sut.create_request("/", raw_data)
        get_payload.assert_called_once_with(raw_data, {})
