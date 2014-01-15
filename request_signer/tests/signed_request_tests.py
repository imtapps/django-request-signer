import json
import mock

from django import test
from django import http
from django.test.utils import override_settings

from request_signer import models, constants
from request_signer.validator import SignatureValidator
from request_signer.decorators import signature_required, has_valid_signature


class SignedRequestTests(test.TestCase):

    @property
    def view(self):
        return lambda request, *args, **kwargs: http.HttpResponse("Completed Test View!")

    def get_request(self, data=None):
        return test.client.RequestFactory().get('/', data=data or {})

    def test_returns_400_response_when_request_doesnt_have_signature_in_data(self):
        request = self.get_request()

        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)

    def test_adds_signature_required_attribute_to_view(self):
        self.assertFalse(hasattr(self.view, 'signature_required'))
        signed_view = signature_required(self.view)
        self.assertTrue(getattr(signed_view, 'signature_required', False))

    def test_returns_400_response_when_request_doesnt_have_client_id_in_data(self):
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
        })

        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)

    @mock.patch('apysigner.get_signature')
    def test_returns_400_when_signature_doesnt_match(self, get_signature):
        get_signature.return_value = 'ABCDEFGHIJKLMNOPQRSTUVWXYZFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)

    @mock.patch('apysigner.get_signature')
    def test_returns_200_view_return_value_when_signature_matches(self, get_signature):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(200, response.status_code)

    @mock.patch('request_signer.signals.successful_signed_request.send')
    @mock.patch('apysigner.get_signature')
    def test_fires_successful_signed_request_signal_from_signature_required_decorator(self, get_signature, send_signal):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })

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

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        instance = SignatureValidator(request)
        with mock.patch('request_signer.decorators.get_validator', mock.Mock(return_value=instance)):
            self.assertTrue(has_valid_signature(request))
        send_signal.assert_called_once_with(sender=instance, request=request)

    @mock.patch('request_signer.signals.successful_signed_request.send')
    @mock.patch('apysigner.get_signature')
    def test_does_not_fire_successful_signal_from_signature_required_when_invalid(self, get_signature, send_signal):
        get_signature.return_value = 'ABCDEFGHIJKLMNOPQRSTUVWXYZFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)
        self.assertFalse(send_signal.called)

    @mock.patch('request_signer.signals.successful_signed_request.send')
    @mock.patch('apysigner.get_signature')
    def test_does_not_fire_successful_signal_from_has_valid_signature_when_invalid(self, get_signature, send_signal):
        get_signature.return_value = 'ABCDEFGHIJKLMNOPQRSTUVWXYZFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        self.assertFalse(has_valid_signature(request))
        self.assertFalse(send_signal.called)

    @mock.patch('apysigner.get_signature')
    def test_calls_create_signature_properly_with_get_data(self, get_signature):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = test.client.RequestFactory().get('/my/path/', data={
            'username': 'tester',
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        signed_view = signature_required(self.view)
        signed_view(request)

        get_signature.assert_called_once_with(client.private_key, request.get_full_path(), None)

    @mock.patch('apysigner.get_signature')
    def test_calls_create_signature_properly_with_no_content_type(self, get_signature):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = test.client.RequestFactory().get('/my/path/', data={
            'username': 'tester',
            constants.SIGNATURE_PARAM_NAME: '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        if 'CONTENT_TYPE' in request.META:
            del request.META['CONTENT_TYPE']
        signed_view = signature_required(self.view)
        signed_view(request)

        get_signature.assert_called_once_with(client.private_key, request.get_full_path(), None)

    @mock.patch('apysigner.get_signature')
    def test_json_is_properly_parsed_into_signature(self, get_signature):
        signature = 'QEw8WN5YzbWlct5ZXH3GIumeiL8m4NErPtXOz_jWexc='
        get_signature.return_value = signature

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        url = "/my/path/?{}={}&{}={}".format(
            constants.SIGNATURE_PARAM_NAME, signature, constants.CLIENT_ID_PARAM_NAME, client.client_id
        )
        data = {'our': 'data', 'goes': 'here'}
        json_string = json.dumps(data)
        request = test.client.RequestFactory().post(url, data=json_string, content_type="application/json")
        signed_view = signature_required(self.view)
        signed_view(request)

        get_signature.assert_called_once_with(client.private_key, request.get_full_path(), json_string)

    @mock.patch('apysigner.get_signature')
    def test_calls_create_signature_properly_with_post_data(self, get_signature):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')

        url = '/my/path/?'
        url += constants.SIGNATURE_PARAM_NAME + '=4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        url += "&" + constants.CLIENT_ID_PARAM_NAME + "=" + client.client_id

        request = test.client.RequestFactory().post(url, data={'username': 'tester'})
        signed_view = signature_required(self.view)
        signed_view(request)

        get_signature.assert_called_once_with(client.private_key, request.get_full_path(), request.POST)

    @mock.patch('apysigner.get_signature')
    def test_does_not_create_signature_with_multivalue_dict_to_prevent_data_loss(self, get_signature):
        get_signature.return_value = '4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')

        url = '/my/path/?'
        url += constants.SIGNATURE_PARAM_NAME + '=4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI='
        url += "&" + constants.CLIENT_ID_PARAM_NAME + "=" + client.client_id

        request = test.client.RequestFactory().post(url, data={
            'usernames': ['t1', 't2', 't3']})
        signed_view = signature_required(self.view)
        signed_view(request)

        get_signature.assert_called_once_with(client.private_key, request.get_full_path(), request.POST)
        posted_data = get_signature.mock_calls[0][1][2]
        self.assertEqual([('usernames', ['t1', 't2', 't3'])], posted_data.items())

    def test_signed_views_are_csrf_exempt(self):
        signed_view = signature_required(self.view)
        self.assertTrue(getattr(signed_view, 'csrf_exempt', False))

    @mock.patch('apysigner.get_signature')
    @override_settings(ALLOW_UNSIGNED_REQUESTS=True)
    def test_returns_200_when_signature_doesnt_match_but_allow_unsigned_is_true(self, get_signature):
        get_signature.return_value = 'ABCDEFGHIJKLMNOPQRSTUVWXYZFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(data={
            constants.SIGNATURE_PARAM_NAME: 'YQ==',
            constants.CLIENT_ID_PARAM_NAME: client.client_id,
        })
        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(200, response.status_code)

    def test_patch_requests_still_use_request_body(self):
        url = '/asdf/'
        request = test.client.RequestFactory().post(url, data={
            'usernames': ['t1', 't2', 't3']}, **{'REQUEST_METHOD': "PATCH"})
        request_without_data = test.client.RequestFactory().post(url, data={}, **{'REQUEST_METHOD': "PATCH"})
        validator1 = SignatureValidator(request)
        validator2 = SignatureValidator(request_without_data)
        self.assertNotEqual(validator1.request_data, validator2.request_data)

    def test_patch_requests_return_dict_of_multipart_form_data(self):
        request = test.client.RequestFactory().post('/asdf/', data={
            'usernames': ['t1', 't2', 't3']}, **{'REQUEST_METHOD': "PATCH"})
        expected = {
            u'--BoUnDaRyStRiNg\r\nContent-Disposition: form-data': [u''],
            u' name': [
                u'"usernames"\r\n\r\nt1\r\n--BoUnDaRyStRiNg\r\nContent-Disposition: form-data',
                u'"usernames"\r\n\r\nt2\r\n--BoUnDaRyStRiNg\r\nContent-Disposition: form-data',
                u'"usernames"\r\n\r\nt3\r\n--BoUnDaRyStRiNg--\r\n']}
        self.assertEqual(expected, SignatureValidator(request).request_data)
