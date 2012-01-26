# -*- coding: utf-8 -*-
from django.test.client import Client
from request_signer.client.generic import SignedRequestFactory
from request_signer.models import AuthorizedClient
from lettuce import step

@step(u'Given a client with the client id "([^"]*)" and the private key "([^"]*)"')
def set_client_id(step, client_id, private_key):
    step.scenario.client_id = client_id
    step.scenario.private_key = private_key

@step(u'And that client is registered with the server')
def register_client(step):
    AuthorizedClient.objects.create(
        client_id=step.scenario.client_id,
        private_key=step.scenario.private_key
    )

@step(u'When the client makes a request to the server at "([^"]*)" with no signature')
def make_request(step, url_path):
    client = Client()
    step.scenario.response = client.get(url_path)

@step(u'When the client makes a request to the server at "([^"]*)" with an invalid signature')
def make_request(step, url_path):
    client = Client()
    factory = SignedRequestFactory('GET', step.scenario.client_id, step.scenario.private_key)
    url = factory.build_request_url({}, url_path)
    step.scenario.response = client.get(url + "invalidating=thesignature")

@step(u'When the client makes a request to the server at "([^"]*)" with the correct signature')
def make_request(step, url_path):
    client = Client()

    factory = SignedRequestFactory('GET', step.scenario.client_id, step.scenario.private_key)
    url = factory.build_request_url({}, url_path)
    step.scenario.response = client.get(url)

@step(u'When the client posts a request to the server at "([^"]*)" with the correct signature and the following data:')
def make_request(step, url_path):
    data = step.hashes[0]
    client = Client()
    factory = SignedRequestFactory('POST', step.scenario.client_id, step.scenario.private_key)
    url = factory.build_request_url(data, url_path)
    step.scenario.response = client.post(url, data)

@step(u'When the client posts a request to the server at "([^"]*)" with the correct signature and no data')
def make_request(step, url_path):
    data = {}
    client = Client()
    factory = SignedRequestFactory('POST', step.scenario.client_id, step.scenario.private_key)
    url = factory.build_request_url(data, url_path)
    step.scenario.response = client.post(url, data)

@step(u'Then the server should reply with a "([^"]*)"')
def assert_status_code(step, status_code):
    assert step.scenario.response.status_code == int(status_code), step.scenario.response.status_code
