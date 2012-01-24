from django.utils import unittest
from request_signer import AuthSigner, constants


__all__ = ('AuthSignerTests', )

class AuthSignerTests(unittest.TestCase):

    def setUp(self):
        self.signer = AuthSigner('2')

    def test_returns_payload_qs_sorted_by_dict_keys(self):
        payload = {'one': 'first one', 'two': '2', 'three': '3', 'four': '4'}
        expected_qs = 'four=4&one=first+one&three=3&two=2'
        self.assertEqual(expected_qs, self.signer._encode_payload(payload))

    def test_returns_payload_qs_sorted_by_dict_keys_and_vals(self):
        payload = {'one': '1', 'two': '2', 'three': '3', 'four': ['8', '4', '0']}
        expected_qs = 'four=0&four=4&four=8&one=1&three=3&two=2'
        self.assertEqual(expected_qs, self.signer._encode_payload(payload))

    def test_returns_payload_qs_sorted_by_first_tuple_item(self):
        payload = [('one', 'first one'), ('two', '2'), ('three', '3'), ('four', '4')]
        expected_qs = 'four=4&one=first+one&three=3&two=2'
        self.assertEqual(expected_qs, self.signer._encode_payload(payload))

    def test_returns_payload_qs_sorted_by_first_tuple_item_and_vals(self):
        payload = [('one', '1'), ('two', '2'), ('three', '3'), ('four', ['8', '4', '0'])]
        expected_qs = 'four=0&four=4&four=8&one=1&three=3&two=2'
        self.assertEqual(expected_qs, self.signer._encode_payload(payload))

    def test_returns_payload_qs_sorted_by_first_tuple_item_and_vals_when_item_repeats(self):
        payload = [('one', '1'), ('two', 'two'), ('two', '2'), ('two', 'dos')]
        expected_qs = 'one=1&two=2&two=dos&two=two'
        self.assertEqual(expected_qs, self.signer._encode_payload(payload))

    def test_returns_empty_string_when_payload_is_none(self):
        self.assertEqual('', self.signer._encode_payload(None))

    def test_returns_empty_string_when_payload_is_empty(self):
        self.assertEqual('', self.signer._encode_payload({}))
        self.assertEqual('', self.signer._encode_payload([]))
        self.assertEqual('', self.signer._encode_payload(()))
        self.assertEqual('', self.signer._encode_payload(''))

    def test_signs_request(self):
        signer = AuthSigner('CoVTr95Xv2Xlu4ZjPo2bWl7u4SnnAMAD7EFFBMS4Dy4=')
        data = {'username': 'some tester', 'first_name': 'Mr. Test'}
        signature = signer.create_signature('http://www.example.com/accounts/user/add/', data)

        expected_signature = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        self.assertEqual(expected_signature, signature)

    def test_classmethod_signs_request(self):
        private_key = 'CoVTr95Xv2Xlu4ZjPo2bWl7u4SnnAMAD7EFFBMS4Dy4='
        base_url = 'http://www.example.com/accounts/user/add/'
        data = {'username': 'some tester', 'first_name': 'Mr. Test'}
        signature = AuthSigner.get_signature(private_key, base_url, data)

        expected_signature = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        self.assertEqual(expected_signature, signature)

    def test_classmethod_generates_signature_excluding_signature_param_in_querystring(self):
        private_key = 'CoVTr95Xv2Xlu4ZjPo2bWl7u4SnnAMAD7EFFBMS4Dy4='
        expected_signature = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        base_url = 'http://www.example.com/accounts/user/add/?'
        base_url += constants.SIGNATURE_PARAM_NAME + "=" + expected_signature
        data = {
            'username': 'some tester',
            'first_name': 'Mr. Test',
        }
        signature = AuthSigner.get_signature(private_key, base_url, data)
        self.assertEqual(expected_signature, signature)

    def test_classmethod_generates_signature_excluding_signature_param_in_payload(self):
        private_key = 'CoVTr95Xv2Xlu4ZjPo2bWl7u4SnnAMAD7EFFBMS4Dy4='
        expected_signature = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        base_url = 'http://www.example.com/accounts/user/add/'
        data = {
            'username': 'some tester',
            'first_name': 'Mr. Test',
            constants.SIGNATURE_PARAM_NAME: expected_signature,
        }
        signature = AuthSigner.get_signature(private_key, base_url, data)
        self.assertEqual(expected_signature, signature)

    def test_signs_request_when_private_key_is_unicode(self):
        # test to ensure we handle private key properly no matter what kind of character
        # encoding the private key is given as:
        # http://bugs.python.org/issue4329  (not a bug, but this is the situation and explanation)
        signer = AuthSigner(u'CoVTr95Xv2Xlu4ZjPo2bWl7u4SnnAMAD7EFFBMS4Dy4=')
        signature = signer.create_signature('http://www.example.com/accounts/user/add/')

        expected_signature = '2ZzgF8AGioIfYzPqedI0FfJKEDG2asRA1LR70q4IOYs='
        self.assertEqual(expected_signature, signature)

    def test_requires_private_key(self):
        with self.assertRaises(Exception) as context:
            AuthSigner(None)

        self.assertEqual(context.exception.message, 'Private key is required.')
