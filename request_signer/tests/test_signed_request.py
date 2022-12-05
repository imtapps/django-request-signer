import json
import re

import django
import six

if six.PY3:
    from urllib.parse import unquote
    from unittest import mock
else:
    from urllib import unquote
    import mock

from django import test
from django import http
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured
from apysigner import get_signature

from request_signer import constants
from request_signer.validator import SignatureValidator
from request_signer.decorators import signature_required, has_valid_signature

TEST_PRIVATE_KEY = 'abc123=='


@override_settings(API_KEYS={'apps-testclient': TEST_PRIVATE_KEY})
class SignedRequestTests(test.TestCase):

    @property
    def view(self):
        return lambda request, *args, **kwargs: http.HttpResponse("Completed Test View!")

    def get_request(self, data=None):
        return test.client.RequestFactory().get('/', data=data or {})

    def test_returns_400_response_when_request_doesnt_have_any_data(self):
        response = self.client.get('/test/')
        self.assertEqual(400, response.status_code)

    def test_returns_400_response_when_request_doesnt_have_signature_in_data(self):
        response = self.client.get('/test/?{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME))
        self.assertEqual(400, response.status_code)

    def test_adds_signature_required_attribute_to_view(self):
        self.assertFalse(hasattr(self.view, 'signature_required'))
        signed_view = signature_required(self.view)
        self.assertTrue(getattr(signed_view, 'signature_required', False))

    def test_returns_400_response_when_request_doesnt_have_client_id_in_data(self):
        response = self.client.get('/test/?{}=anythingherethatiswrong'.format(constants.SIGNATURE_PARAM_NAME))
        self.assertEqual(400, response.status_code)

    def test_returns_400_when_signature_doesnt_match(self):
        response = self.client.get(
            '/test/?{}=apps-testclient&{}=anythingherethatiswrong'.format(
                constants.CLIENT_ID_PARAM_NAME, constants.SIGNATURE_PARAM_NAME
            )
        )
        self.assertEqual(400, response.status_code)

    def test_returns_200_view_return_value_when_signature_matches(self):
        url = '/test/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(200, response.status_code)

    def test_signature_works_when_url_contains_spaces_and_querystring_contains_escaped_chars(self):
        url = '/test/a b c/?username=test%2C&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(200, response.status_code)

    def test_signature_works_when_url_contains_spaces(self):
        url = '/test/a b c/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(200, response.status_code)

    def test_signature_works_when_url_contains_escapsed_spaces(self):
        url = '/test/a%20b%20c/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(200, response.status_code)

    @mock.patch('request_signer.signals.successful_signed_request.send')
    @mock.patch('apysigner.get_signature')
    def test_fires_successful_signed_request_signal_from_signature_required_decorator(self, get_signature, send_signal):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        request = self.get_request(
            data={
                constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
                constants.CLIENT_ID_PARAM_NAME: 'apps-testclient',
            }
        )
        instance = SignatureValidator(request)
        with mock.patch('request_signer.decorators.get_validator', mock.Mock(return_value=instance)):
            signed_view = signature_required(self.view)
            response = signed_view(request)
        self.assertEqual(200, response.status_code)
        send_signal.assert_called_once_with(sender=instance, request=request)

    @mock.patch('request_signer.signals.successful_signed_request.send')
    @mock.patch('apysigner.get_signature')
    def test_fires_successful_signed_request_signal_from_has_valid_signature(self, get_signature, send_signal):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        request = self.get_request(
            data={
                constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
                constants.CLIENT_ID_PARAM_NAME: 'apps-testclient',
            }
        )
        instance = SignatureValidator(request)
        with mock.patch('request_signer.decorators.get_validator', mock.Mock(return_value=instance)):
            self.assertTrue(has_valid_signature(request))
        send_signal.assert_called_once_with(sender=instance, request=request)

    @mock.patch('request_signer.signals.successful_signed_request.send')
    def test_does_not_fire_successful_signal_from_signature_required_when_invalid(self, send_signal):
        response = self.client.get(
            '/test/?{}=apps-testclient&{}=anythingherethatiswrong'.format(
                constants.CLIENT_ID_PARAM_NAME, constants.SIGNATURE_PARAM_NAME
            )
        )
        self.assertEqual(400, response.status_code)
        self.assertFalse(send_signal.called)

    @mock.patch('request_signer.signals.successful_signed_request.send')
    @mock.patch('apysigner.get_signature')
    def test_does_not_fire_successful_signal_from_has_valid_signature_when_invalid(self, get_signature, send_signal):
        get_signature.return_value = 'ABCDEFGHIJKLMNOPQRSTUVWXYZFtYkCdi4XAc-vOLtI='
        request = self.get_request(
            data={
                constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
                constants.CLIENT_ID_PARAM_NAME: 'apps-testclient',
            }
        )
        self.assertFalse(has_valid_signature(request))
        self.assertFalse(send_signal.called)

    def test_calls_create_signature_properly_with_get_data(self):
        url = '/test/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(200, response.status_code)

    def test_calls_create_signature_properly_with_get_data_and_with_an_at_symbol(self):
        url = '/test/?username=test@example.com&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(200, response.status_code)

    @mock.patch('apysigner.get_signature')
    def test_calls_create_signature_properly_with_no_content_type(self, get_signature):
        signature = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        get_signature.return_value = signature
        request = test.client.RequestFactory().get(
            "/my/path/?{}={}&{}={}".format(
                constants.CLIENT_ID_PARAM_NAME,
                'apps-testclient',
                constants.SIGNATURE_PARAM_NAME,
                signature,
            )
        )
        if 'CONTENT_TYPE' in request.META:
            del request.META['CONTENT_TYPE']
        signed_view = signature_required(self.view)
        signed_view(request)
        call_url = unquote(request.get_full_path())
        call_url = re.sub(r'&__signature={}$'.format(signature), '', call_url, count=1)
        get_signature.assert_called_once_with(TEST_PRIVATE_KEY, call_url, {})

    @mock.patch('apysigner.get_signature')
    def test_json_is_properly_parsed_into_signature(self, get_signature):
        signature = 'QEw8WN5YzbWlct5ZXH3GIumeiL8m4NErPtXOz_jWexc='
        url = "/my/path/?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            'apps-testclient',
            constants.SIGNATURE_PARAM_NAME,
            signature,
        )
        data = {'our': 'data', 'goes': 'here'}
        json_string = json.dumps(data)
        request = test.client.RequestFactory().post(url, data=json_string, content_type="application/json")
        signed_view = signature_required(self.view)
        signed_view(request)
        get_signature.assert_called_with(TEST_PRIVATE_KEY, '/my/path/?__client_id=apps-testclient', json_string)

    def test_json_payload_is_valid(self):
        json_string = json.dumps({'our': 'data', 'goes': 'here'})
        url = '/test/?username=test@example.com&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, json_string)
        response = self.client.post(
            '{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature),
            json_string,
            content_type="application/json"
        )
        self.assertEqual(200, response.status_code)

    @mock.patch('apysigner.get_signature')
    def test_calls_create_signature_properly_with_post_data(self, get_signature):
        signature = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        url = "/my/path/?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            'apps-testclient',
            constants.SIGNATURE_PARAM_NAME,
            signature,
        )
        request = test.client.RequestFactory().post(url, data={'username': 'tester'})
        signed_view = signature_required(self.view)
        signed_view(request)
        get_signature.assert_called_once_with(
            TEST_PRIVATE_KEY, '/my/path/?__client_id=apps-testclient', dict(request.POST)
        )

    def test_post_data_payload_is_valid(self):
        data = {'username': ['tester']}
        url = '/test/?{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, payload=data)
        response = self.client.post('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature), data=data)
        self.assertEqual(200, response.status_code)

    @mock.patch('apysigner.get_signature')
    def test_does_not_create_signature_with_multivalue_dict_to_prevent_data_loss(self, get_signature):
        signature = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        url = "/my/path/?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            'apps-testclient',
            constants.SIGNATURE_PARAM_NAME,
            signature,
        )
        request = test.client.RequestFactory().post(url, data={'usernames': ['t1', 't2', 't3']})
        signed_view = signature_required(self.view)
        signed_view(request)

        expected_url = re.sub(r'&__signature={}$'.format(signature), '', unquote(request.get_full_path()), count=1)
        get_signature.assert_called_once_with(TEST_PRIVATE_KEY, expected_url, dict(request.POST))
        posted_data = get_signature.mock_calls[0][1][2]
        self.assertEqual([('usernames', ['t1', 't2', 't3'])], list(posted_data.items()))

    def test_post_multivalue_data_payload_is_valid(self):
        data = {'username': ['tester', 'billyjean']}
        url = '/test/?{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, payload=data)
        response = self.client.post('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature), data=data)
        self.assertEqual(200, response.status_code)

    def test_signed_views_are_csrf_exempt(self):
        signed_view = signature_required(self.view)
        self.assertTrue(getattr(signed_view, 'csrf_exempt', False))

    @override_settings(ALLOW_UNSIGNED_REQUESTS=True)
    def test_returns_200_when_signature_doesnt_match_but_allow_unsigned_is_true(self):
        response = self.client.get(
            '/test/?{}=apps-testclient&{}=anythingherethatiswrong'.format(
                constants.CLIENT_ID_PARAM_NAME, constants.SIGNATURE_PARAM_NAME
            )
        )
        self.assertEqual(200, response.status_code)

    def test_put_requests_still_use_request_body(self):
        url = '/asdf/'
        request = test.client.RequestFactory().post(
            url, data={'usernames': ['t1', 't2', 't3']}, **{
                'REQUEST_METHOD': "PUT"
            }
        )
        request_without_data = test.client.RequestFactory().post(url, data={}, **{'REQUEST_METHOD': "PUT"})
        validator1 = SignatureValidator(request)
        validator2 = SignatureValidator(request_without_data)
        self.assertNotEqual(validator1.request_data, validator2.request_data)

    def test_put_json_is_valid(self):
        data = json.dumps({'username': ['tester', 'billyjean']})
        url = '/test/?{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, payload=data)
        response = self.client.put(
            '{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature),
            data=data,
            content_type="application/json"
        )
        self.assertEqual(200, response.status_code)

    def test_patch_requests_still_use_request_body(self):
        url = '/asdf/'
        request = test.client.RequestFactory().post(
            url, data={'usernames': ['t1', 't2', 't3']}, **{
                'REQUEST_METHOD': "PATCH"
            }
        )
        request_without_data = test.client.RequestFactory().post(url, data={}, **{'REQUEST_METHOD': "PATCH"})
        validator1 = SignatureValidator(request)
        validator2 = SignatureValidator(request_without_data)
        self.assertNotEqual(validator1.request_data, validator2.request_data)

    def test_patch_json_is_valid(self):
        data = json.dumps({'username': ['tester', 'billyjean']})
        url = '/test/?{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, payload=data)
        response = self.client.patch(
            '{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature),
            data=data,
            content_type="application/json"
        )
        self.assertEqual(200, response.status_code)

    def test_patch_requests_return_dict_of_multipart_form_data(self):
        request = test.client.RequestFactory().post(
            '/asdf/', data={'usernames': ['t1', 't2', 't3']}, **{
                'REQUEST_METHOD': "PATCH"
            }
        )

        if django.get_version() >= "3.2":
            expected = {
                '--BoUnDaRyStRiNg\r\nContent-Disposition: form-data; name': [
                    '"usernames"\r\n\r\nt1\r\n--BoUnDaRyStRiNg\r\nContent-Disposition: form-data; '
                    'name="usernames"\r\n\r\nt2\r\n--BoUnDaRyStRiNg\r\nContent-Disposition: form-data; '
                    'name="usernames"\r\n\r\nt3\r\n--BoUnDaRyStRiNg--\r\n'
                ]}
        else:
            expected = {
                u'--BoUnDaRyStRiNg\r\nContent-Disposition: form-data': [u''],
                u' name': [
                    u'"usernames"\r\n\r\nt1\r\n--BoUnDaRyStRiNg\r\nContent-Disposition: form-data',
                    u'"usernames"\r\n\r\nt2\r\n--BoUnDaRyStRiNg\r\nContent-Disposition: form-data',
                    u'"usernames"\r\n\r\nt3\r\n--BoUnDaRyStRiNg--\r\n'
                ]
            }

        self.assertEqual(expected, SignatureValidator(request).request_data)

    @mock.patch('apysigner.get_signature')
    def test_json_api_is_properly_parsed_into_signature(self, get_signature):
        signature = 'QEw8WN5YzbWlct5ZXH3GIumeiL8m4NErPtXOz_jWexc='
        url = "/my/path/?{}={}&{}={}".format(
            constants.CLIENT_ID_PARAM_NAME,
            'apps-testclient',
            constants.SIGNATURE_PARAM_NAME,
            signature,
        )
        data = {'our': 'data', 'goes': 'here'}
        json_string = json.dumps(data)
        request = test.client.RequestFactory().post(url, data=json_string, content_type="application/vnd.api+json")
        signed_view = signature_required(self.view)
        signed_view(request)
        get_signature.assert_called_with(TEST_PRIVATE_KEY, '/my/path/?__client_id=apps-testclient', json_string)

    def test_json_api_payload_is_valid(self):
        json_string = json.dumps({'our': 'data', 'goes': 'here'})
        url = '/test/?username=test@example.com&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, json_string)
        response = self.client.post(
            '{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature),
            json_string,
            content_type="application/vnd.api+json"
        )
        self.assertEqual(200, response.status_code)

    def test_put_json_api_is_valid(self):
        data = json.dumps({'username': ['tester', 'billyjean']})
        url = '/test/?{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, payload=data)
        response = self.client.put(
            '{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature),
            data=data,
            content_type="application/vnd.api+json"
        )
        self.assertEqual(200, response.status_code)

    def test_patch_json_api_is_valid(self):
        data = json.dumps({'username': ['tester', 'billyjean']})
        url = '/test/?{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url, payload=data)
        response = self.client.patch(
            '{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature),
            data=data,
            content_type="application/vnd.api+json"
        )
        self.assertEqual(200, response.status_code)

    def test_does_not_call_database_per_request(self):
        url = '/test/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature(TEST_PRIVATE_KEY, url)
        with self.assertNumQueries(0):
            response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
            self.assertEqual(200, response.status_code)

    def test_returns_200_when_using_api_keys(self):
        url = '/test/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature('abc123==', url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(200, response.status_code)

    @override_settings(API_KEYS={'apps-no': TEST_PRIVATE_KEY})
    def test_returns_400_when_using_api_keys_that_do_not_match(self):
        url = '/test/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature('abc123==', url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(400, response.status_code)
        url = '/test/?username=test&{}=app-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
        signature = get_signature('123==', url)
        response = self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
        self.assertEqual(400, response.status_code)


class NoSettingsClass(test.TestCase):

    def test_request_fails_without_correct_settings(self):
        with self.assertRaises(ImproperlyConfigured):
            url = '/test/?username=test&{}=apps-testclient'.format(constants.CLIENT_ID_PARAM_NAME)
            signature = get_signature('abc123==', url)
            self.client.get('{}&{}={}'.format(url, constants.SIGNATURE_PARAM_NAME, signature))
