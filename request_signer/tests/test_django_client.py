import six

if six.PY3:
    from unittest import mock
else:
    import mock

from django import test
from request_signer.client.generic import Client
from request_signer.client.generic.django_client import DjangoClient


class DjangoClientTests(test.TestCase):

    sut_class = DjangoClient

    def setUp(self):
        self.django_backend_patch = mock.patch(
            'request_signer.client.generic.django_backend.DjangoSettingsApiCredentialsBackend'
        )
        self.django_backend = self.django_backend_patch.start()

    def tearDown(self):
        self.django_backend_patch.stop()

    def test_api_credentials_created_from_django_backend_with_the_client(self):
        with mock.patch.object(Client, '__init__'):
            sut = self.sut_class()
        self.django_backend.assert_called_once_with(sut)

    def test_invokes_super_init_with_django_backend(self):
        with mock.patch.object(Client, '__init__') as init:
            self.sut_class()
        init.assert_called_once_with(self.django_backend.return_value)
