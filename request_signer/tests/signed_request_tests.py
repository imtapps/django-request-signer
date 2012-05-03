import mock

from django import test
from django import http

from request_signer import  models, constants
from request_signer.decorators import signature_required, check_signature

__all__ = (
    'SignedRequestTests',
    'CheckSignatureTests',
)


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
            constants.SIGNATURE_PARAM_NAME:'4ZAQJqmWE_C9ozPkpJ3Owh0Z_DFtYkCdi4XAc-vOLtI=',
        })

        signed_view = signature_required(self.view)
        response = signed_view(request)
        self.assertEqual(400, response.status_code)

    @mock.patch('request_signer.signer.SignatureMaker.get_signature')
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



class CheckSignatureTests(test.TestCase):

    def setUp(self):
        self.TEST_PRIVATE_KEY = 'UHJpdmF0ZSBLZXk='
        self.url_one = "/example/get-it/?q=find"
        self.url_two = "/example/post-it/"
        self.url_post_data = {'q': 'update'}

        # valid signatures for urls above and data
        self.signature_one = "T-lT3uT2wpUobJvDkXpxtsEAl7KmrEg6k3So_Varya8="
        self.signature_two = "AKm9ZGCZPaYRMnLxpFZ8-ulaCIr_wKYAruZVm36uv3Q="

    def test_returns_true_when_signatures_match_and_no_post_data(self):
        signature_valid = check_signature(self.signature_one, self.TEST_PRIVATE_KEY, self.url_one, None)
        self.assertEqual(True, signature_valid)

    def test_returns_true_when_signatures_match_and_has_post_data(self):
        signature_valid = check_signature(self.signature_two, self.TEST_PRIVATE_KEY, self.url_two, self.url_post_data)
        self.assertEqual(True, signature_valid)

    def test_returns_false_when_signatures_dont_match(self):
        bad_signature = "ABCc0hS02rVC3016krevud1aW9B6Ls0Tp4_XcezuXYZ="
        signature_valid = check_signature(bad_signature, self.TEST_PRIVATE_KEY, self.url_one, None)
        self.assertEqual(False, signature_valid)

    def test_doesnt_use_signature_already_in_url_to_check_for_valid_signature(self):
        url_with_sig = "{url}&{signature_param}={signature}".format(
            url=self.url_one,
            signature_param=constants.SIGNATURE_PARAM_NAME,
            signature=self.signature_one,
        )

        signature_valid = check_signature(self.signature_one, self.TEST_PRIVATE_KEY, url_with_sig, None)
        self.assertEqual(True, signature_valid)

    def test_doesnt_use_signature_already_in_url_to_check_for_valid_signature_with_post_data(self):
        url_with_sig = "{url}?{signature_param}={signature}".format(
            url=self.url_two,
            signature_param=constants.SIGNATURE_PARAM_NAME,
            signature=self.signature_two,
        )

        signature_valid = check_signature(self.signature_two, self.TEST_PRIVATE_KEY, url_with_sig, self.url_post_data)
        self.assertEqual(True, signature_valid)
