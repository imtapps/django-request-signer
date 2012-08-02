from collections import OrderedDict
from django.utils import unittest
from request_signer.client.generic.base import default_encoding


class DefaultEncodingTests(unittest.TestCase):

    def test_encodes_dict_of_data(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', 2), ('c', 'asdf'))))
        self.assertEqual('a=1&b=2&c=asdf', result)

    def test_encodes_dict_with_nested_list(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', [2, 4]), ('c', 'asdf'))))
        self.assertEqual('a=1&b=2&b=4&c=asdf', result)

    def test_encodes_dict_with_nested_empty_list(self):
        result = default_encoding(OrderedDict((('a', 1), ('b', []), ('c', 'asdf'))))
        self.assertEqual('a=1&c=asdf', result)
