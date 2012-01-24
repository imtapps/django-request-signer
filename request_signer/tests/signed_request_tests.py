import mock
from django import test
from django import http
from request_signer import signature_required, models, constants

__all__ = ('SignedRequestTests', )

class SignedRequestTests(test.TestCase):
    """
    Tests for the signature_required decorator.
    """

    @property
    def view(self):
        """
        A fake view that returns a proper 200 response.
        """
        return lambda request, *args, **kwargs: http.HttpResponse("Completed Test View!")

    def get_request(self, data=None, **headers):
        return test.client.RequestFactory(**headers).get('/', data=data or {})

    def test_returns_400_response_when_request_doesnt_have_signature_header(self):
        request = self.get_request(
            HTTP_X_APPS_AUTH_CLIENT_ID='apps-something',
        )

        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)

    def test_returns_400_response_when_request_doesnt_have_client_id_header(self):
        request = self.get_request(
            HTTP_X_APPS_AUTH_SIGNATURE='4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
        )

        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)

    @mock.patch('request_signer.AuthSigner.get_signature')
    def test_returns_400_when_signature_doesnt_match(self, get_signature):
        get_signature.return_value = 'ABCDEFGHIJKLMNOPQRSTUVWXYZFtYkCdi4XAc-vOLtI='

        client = models.AuthorizedClient.objects.create(client_id='apps-testclient')
        request = self.get_request(
            HTTP_X_APPS_AUTH_SIGNATURE='4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
            HTTP_X_APPS_AUTH_CLIENT_ID=client.client_id,
        )
        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)

    @mock.patch('request_signer.AuthSigner.get_signature')
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

    @mock.patch('request_signer.AuthSigner.get_signature')
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

    @mock.patch('request_signer.AuthSigner.get_signature')
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

    def test_signed_views_are_csrf_exempt(self):
        signed_view = signature_required(self.view)
        self.assertTrue(getattr(signed_view, 'csrf_exempt', False))
