import json

from django import test
from django import http
from django.conf.urls import url, patterns
from django.views.decorators.csrf import csrf_exempt

from request_signer.client.generic import WebException
from request_signer.client.generic.json_api import BaseDjangoJsonApiClient


class Settings(object):

    def __init__(self, server_url):
        self.client_id = 'dev'
        self.private_key = 'YQ=='
        self.base_url = server_url


@csrf_exempt
def items(request, pk=None):
    data = {'data': [
        {'attributes': {'name': 'Item 1'}, 'id': 1, 'type': 'Item'},
        {'attributes': {'name': 'Item 2'}, 'id': 2, 'type': 'Item'}
    ]}
    if pk or request.method in ['PATCH', 'POST']:
        data = {'data': {'attributes': {'name': 'Item 2'}, 'id': 2, 'type': 'Item'}}
    if request.method == 'DELETE':
        return http.HttpResponse(status=204, content_type='application/vnd.api+json')
    return http.HttpResponse(json.dumps(data), content_type='application/vnd.api+json')


class BaseDjangoJsonApiClientTests(test.LiveServerTestCase):
    urls = patterns(
        '',
        url(r'^item/$', items),
        url(r'^item/(?P<pk>[0-9]+)/$', items),
        url(r'^exception/$', lambda request: 'x'.items()),
    )

    def setUp(self):
        self.json_api_client = BaseDjangoJsonApiClient(9690, Settings(self.live_server_url))

    def test_get_list_of_items(self):
        expected = {'data': [
            {'attributes': {'name': 'Item 1'}, 'id': 1, 'type': 'Item'},
            {'attributes': {'name': 'Item 2'}, 'id': 2, 'type': 'Item'}
        ]}
        response = self.json_api_client.get('item')
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.json)

    def test_get_specific_item(self):
        expected = {'data': {'attributes': {'name': 'Item 2'}, 'id': 2, 'type': 'Item'}}
        response = self.json_api_client.get('item', 2)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.json)

    def test_exception_can_be_set_in_subclasses(self):
        class TestException(WebException):
            pass

        class TestClient(BaseDjangoJsonApiClient):
            EXCEPTION_TYPE = TestException

        client = TestClient(9690, Settings(self.live_server_url))
        with self.assertRaises(TestException):
            client.get('exception')

    def test_update_specific_item(self):
        data = {'data': {'attributes': {'name': 'Item 2'}, 'id': 2, 'type': 'Item'}}
        response = self.json_api_client.update('item', 1, data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(data, response.json)

    def test_create_new_item(self):
        data = {'data': {'attributes': {'name': 'Item 2'}, 'type': 'Item'}}
        response = self.json_api_client.create('item', data)
        expected = {'data': {'attributes': {'name': 'Item 2'}, 'id': 2, 'type': 'Item'}}
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.json)

    def test_delete_specific_item(self):
        response = self.json_api_client.delete('item', 2)
        self.assertEqual(204, response.status_code)
