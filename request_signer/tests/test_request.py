from django import test
from request_signer.client.generic import Request, HttpMethodNotAllowed


class RequestTests(test.TestCase):

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
