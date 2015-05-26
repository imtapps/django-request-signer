
import mock

from django import test
from django.core.management.base import CommandError

from request_signer.management.commands import createclient
from request_signer.models import create_private_key, AuthorizedClient


class CreateClientTests(test.TestCase):

    def setUp(self):
        self.command = createclient.Command()

    def test_requires_client_in_options(self):
        with self.assertRaises(CommandError) as e:
            self.command.handle()
        self.assertEqual("Client is required.", e.exception.message)

    def test_requires_client_to_be_not_empty(self):
        with self.assertRaises(CommandError) as e:
            self.command.handle(client="")
        self.assertEqual("Client is required.", e.exception.message)

    def test_creates_client_with_key_provided(self):
        key = create_private_key()

        self.command.execute(client="client", key=key)

        c = AuthorizedClient.objects.get(client_id="client")
        self.assertEqual(key, c.private_key)

    @mock.patch("request_signer.management.commands.createclient.create_private_key")
    def test_creates_new_private_key_when_not_given(self, create_private_key):
        create_private_key.return_value = "some private key"

        self.command.execute(client="client")

        c = AuthorizedClient.objects.get(client_id="client")
        self.assertEqual("some private key", c.private_key)
        create_private_key.assert_called_once_with()
