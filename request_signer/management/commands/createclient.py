
from optparse import make_option

from django.core.management import BaseCommand, CommandError
from request_signer.models import AuthorizedClient, create_private_key


class Command(BaseCommand):
    help = "Creates an authorized client. You can provide the exact private key"\
           "to use, or the command will auto generate one if not provided."

    option_list = BaseCommand.option_list + (
        make_option("-c", "--client", dest="client", action="store"),
        make_option("-k", "--key", dest="key", action="store"),
    )

    def handle(self, *args, **options):
        client = options.get("client")
        key = options.get("key")
        if not client:
            raise CommandError("Client is required.")

        if not key:
            key = create_private_key()

        client = AuthorizedClient.objects.create(client_id=client, private_key=key)
        self.stdout.write("\nYour client id is: '{0}'\n".format(client.client_id))
        self.stdout.write("Your private key is: '{0}'\n".format(client.private_key))
