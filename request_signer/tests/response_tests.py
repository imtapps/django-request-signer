from cStringIO import StringIO
import httplib
import json
import mock
from django.utils import unittest
from request_signer.client.generic import  Response

__all__ = ('ResponseTests', )

class ResponseTests(unittest.TestCase):

    def setUp(self):
        self.raw_response = mock.Mock()
        self.response = Response(self.raw_response)

    def test_response_requires_url_to_init(self):
        self.assertEqual(self.response.raw_response, self.raw_response)

    @mock.patch.object(Response, '_evaluate_response_code_for_success')
    def test_response_is_successful_returns_value_from_evaluate(self, evaluate_response):
        self.assertEqual(self.response.is_successful, evaluate_response.return_value)

    @mock.patch.object(Response, 'status_code', mock.Mock())
    @mock.patch.object(Response, '_evaluate_response_code_for_success')
    def test_response_is_successful_calls_evaluate_with_status_code(self, evaluate_response):
        getattr(self.response, 'is_successful')
        evaluate_response.assert_called_once_with(self.response.status_code)

    def test_bad_http_status_return_false_from_evaluate_response_code_for_success(self):
        include_status = lambda status: status < 200 or status > 299
        self.evaluate_response_code_for_success(False, include_status)

    def test_good_http_status_return_true_from_evaluate_response_code_for_success(self):
        include_status = lambda status: 199 < status < 300
        self.evaluate_response_code_for_success(True, include_status)

    def evaluate_response_code_for_success(self, expected, include_status):
        statuses = (status for status in httplib.responses.keys() if include_status(status))
        for response_code in statuses:
            value = self.response._evaluate_response_code_for_success(response_code)
            self.assertEqual(expected, value, "it seems '%s' returned '%s' for some odd reason" % (response_code, value))

    def test_status_code_returns_status_code_from_raw_response(self):
        self.raw_response.code = 201
        self.assertEqual(201, self.response.status_code)

    def test_returns_dict_of_json_data_from_response(self):
        self.raw_response.read.return_value = '{"first":"item"}'
        self.assertEqual(dict(first='item'), self.response.json)

    def test_returns_empty_dict_when_response_is_empty_string(self):
        self.raw_response.read.return_value = ''
        self.assertEqual({}, self.response.json)

    def test_can_read_response_multiple_times(self):
        data = '{"data": "this is the response"}'
        expected = json.loads(data)
        self.response.raw_response = StringIO(data)
        self.assertEqual(expected, self.response.json)
        self.assertEqual(expected, self.response.json)

