
import six

if six.PY3:
    from unittest import mock
else:
    import mock

from django import test
from request_signer.client.generic import Response, WebException

from django.test.utils import override_settings
from request_signer.client.generic.rest import BaseDjangoRestClient


class BaseDjangoRestClientTests(test.TestCase):

    def setUp(self):
        self.sut = BaseDjangoRestClient()
        self.sut.BASE_API_ENDPOINT = "/api/"

    def get_mock_response(self, **kwargs):
        return mock.MagicMock(Response, autospec=True, **kwargs)

    def test_build_endpoint_returns_endpoint_when_only_group_provided(self):
        endpoint = self.sut.build_endpoint("1234")
        self.assertEqual("/api/1234/", endpoint)

    def test_build_endpoint_returns_endpoint_when_group_and_item_provided(self):
        endpoint = self.sut.build_endpoint("1234", "item-detail")
        self.assertEqual("/api/1234/item-detail/", endpoint)

    def test_get_json_response_gets_response_with_accept_header(self):
        endpoint = self.sut.build_endpoint("1234", "item-detail")
        data = {"some_data": "lives here"}

        with mock.patch.object(self.sut, "_get_response") as get_response:
            self.sut._get_json_response("GET", endpoint, data)
        get_response.assert_called_once_with("GET", endpoint, data, headers={"Accept": "application/json"})

    def test_get_list_issues_get_json_response_for_endpoint(self):
        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            self.sut.get_list("1234")
        get_response.assert_called_once_with("GET", "/api/1234/")

    def test_get_list_returns_json_response_when_successful(self):
        response = self.get_mock_response()

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.get_list("1234")
        self.assertEqual(response.json, result)

    def test_get_list_returns_json_response_when_404(self):
        response = self.get_mock_response(status_code=404, is_successful=False)

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.get_list("1234")
        self.assertEqual(response.json, result)

    def test_get_list_raises_web_exception_when_not_successful(self):
        response = self.get_mock_response(status_code=500, is_successful=False)

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            with self.assertRaises(WebException) as e:
                self.sut.get_list("1234")
        self.assertEqual(str(response.read.return_value), str(e.exception.message))

    def test_get_item_issues_get_json_response_for_endpoint(self):
        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            self.sut.get_item("1234", "pk-3")
        get_response.assert_called_once_with("GET", "/api/1234/pk-3/")

    def test_get_item_returns_json_response_when_successful(self):
        response = self.get_mock_response()

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.get_item("1234", "pk-3")
        self.assertEqual(response.json, result)

    def test_get_item_returns_json_response_when_404(self):
        response = self.get_mock_response(status_code=404, is_successful=False)

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.get_item("1234", "pk-3")
        self.assertEqual(response.json, result)

    def test_get_item_raises_web_exception_when_not_successful(self):
        response = self.get_mock_response(status_code=500, is_successful=False)

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            with self.assertRaises(WebException) as e:
                self.sut.get_item("1234", "pk-3")
        self.assertEqual(str(response.read.return_value), str(e.exception.message))

    def test_create_issues_get_json_response_for_endpoint(self):
        data = {'some_data': 'to send'}
        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            self.sut.create("1234", **data)
        get_response.assert_called_once_with("POST", "/api/1234/", data=data)

    def test_create_returns_json_response_when_successful(self):
        response = self.get_mock_response()
        data = {'some_data': 'to send'}

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.create("1234", **data)
        self.assertEqual(response.json, result)

    def test_create_raises_web_exception_when_not_successful(self):
        response = self.get_mock_response(status_code=400, is_successful=False)
        data = {'some_data': 'to send'}

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            with self.assertRaises(WebException) as e:
                self.sut.create("1234", **data)
        self.assertEqual(str(response.read.return_value), str(e.exception.message))

    def test_update_issues_get_json_response_for_endpoint(self):
        data = {'some_data': 'to send'}
        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            self.sut.update("1234", "pk-3", **data)

        expected_data = dict(data, _method="PUT")
        get_response.assert_called_once_with("POST", "/api/1234/pk-3/", data=expected_data)

    def test_update_returns_json_response_when_successful(self):
        response = self.get_mock_response()
        data = {'some_data': 'to send'}

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.update("1234", "pk-3", **data)
        self.assertEqual(response.json, result)

    def test_update_raises_web_exception_when_not_successful(self):
        response = self.get_mock_response(status_code=404, is_successful=False)
        data = {'some_data': 'to send'}

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            with self.assertRaises(WebException) as e:
                self.sut.update("1234", "pk-3", **data)
        self.assertEqual(str(response.read.return_value), str(e.exception.message))

    def test_delete_issues_get_json_response_for_endpoint(self):
        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            self.sut.delete("1234", "pk-3")
        get_response.assert_called_once_with("POST", "/api/1234/pk-3/", data={"_method": "DELETE"})

    def test_delete_returns_json_response_when_successful(self):
        response = self.get_mock_response()

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.delete("1234", "pk-3")
        self.assertEqual(response.json, result)

    def test_delete_returns_json_response_when_404(self):
        response = self.get_mock_response(status_code=404, is_successful=False)

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            result = self.sut.delete("1234", "pk-3")
        self.assertEqual(response.json, result)

    def test_delete_raises_web_exception_when_not_successful(self):
        response = self.get_mock_response(status_code=500, is_successful=False)

        with mock.patch.object(self.sut, "_get_json_response") as get_response:
            get_response.return_value = response
            with self.assertRaises(WebException) as e:
                self.sut.delete("1234", "pk-3")
        self.assertEqual(str(response.read.return_value), str(e.exception.message))


class BaseDjangoRestClientInitTests(test.TestCase):

    @override_settings(TEST_DOMAIN='my_domain')
    @override_settings(TEST_CLIENT_ID='my_client_id')
    @override_settings(TEST_PRIVATE_KEY='my_private_key')
    def test_uses_django_settings_by_default_for_api_credentials(self):

        class SomeClient(BaseDjangoRestClient):
            domain_settings_name = 'TEST_DOMAIN'
            client_id_settings_name = 'TEST_CLIENT_ID'
            private_key_settings_name = 'TEST_PRIVATE_KEY'

        rest_client = SomeClient()

        self.assertEqual('my_domain', rest_client._base_url)
        self.assertEqual('my_client_id', rest_client._client_id)
        self.assertEqual('my_private_key', rest_client._private_key)

    def test_will_use_provided_settings_when_available(self):

        class SomeProvider(object):
            base_url = "my_domain"
            client_id = "my_client_id"
            private_key = "my_private_key"

        class SomeClient(BaseDjangoRestClient):
            pass

        provider = SomeProvider()
        rest_client = SomeClient(provider)

        self.assertEqual('my_domain', rest_client._base_url)
        self.assertEqual('my_client_id', rest_client._client_id)
        self.assertEqual('my_private_key', rest_client._private_key)
