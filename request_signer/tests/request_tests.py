from urllib import urlencode
import mock
from django.utils import unittest
from request_signer.client.generic import Request, HttpMethodNotAllowed

class RequestTests(unittest.TestCase):

    def get_request(self, http_method, url="http://some.domain.com"):
        return Request(http_method, url, None)

    def assert_sets_http_method(self, http_method):
        request = self.get_request(http_method)
        self.assertEqual(http_method, request.get_method())

    def test_sets_method_to_get_when_passed_to_init(self):
        self.assert_sets_http_method('GET')

    def test_sets_method_to_post_when_passed_to_init(self):
        self.assert_sets_http_method('POST')

    def test_sets_method_to_put_when_passed_to_init(self):
        self.assert_sets_http_method('PUT')

    def test_sets_method_to_delete_when_passed_to_init(self):
        self.assert_sets_http_method('DELETE')

    def test_sets_method_to_head_when_passed_to_init(self):
        self.assert_sets_http_method('HEAD')

    def test_sets_method_to_options_when_passed_to_init(self):
        self.assert_sets_http_method('OPTIONS')

    def test_sets_method_to_trace_when_passed_to_init(self):
        self.assert_sets_http_method('TRACE')

    def test_raises_http_response_not_allowed_when_other_http_method(self):
        with self.assertRaises(HttpMethodNotAllowed):
            self.get_request('GARBAGE')

    def test_get_dict_data_method_returns_dict_of_request_data_for_post_requests(self):
        data = {'some': 'da ta', 'goes': 'he re'}
        sut = Request('POST', 'www.myurl.com', data)
        data_dict = sut.get_data_dict()
        self.assertEqual(data, data_dict)

    def test_get_dict_data_method_returns_dict_of_request_data_for_get_requests(self):
        data = {'some': 'da ta', 'goes': 'he re'}
        sut = Request('GET', 'www.myurl.com', data)
        data_dict = sut.get_data_dict()
        self.assertEqual(None, data_dict)

    @mock.patch('urllib2.Request.__init__')
    def test_urlencodes_data_as_part_of_url_when_method_is_get(self, urllib2_request):
        Request('GET', 'www.myurl.com', {'some':'da ta', 'goes':'he re'})
        self.assertEqual(None, urllib2_request.call_args[0][1])
        self.assertEqual("www.myurl.com?some=da+ta&goes=he+re", urllib2_request.call_args[0][0])

    @mock.patch('urllib2.Request.__init__')
    def test_passes_data_to_urllib_request_when_method_is_not_get(self, urllib2_request):
        data = {'some': 'da ta', 'goes': 'he re'}
        Request('POST', 'www.myurl.com', data)
        self.assertEqual(urlencode(data), urllib2_request.call_args[0][1])
        self.assertEqual("www.myurl.com", urllib2_request.call_args[0][0])

