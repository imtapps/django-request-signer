from request_signer.client.generic import Client, django_backend


class DjangoClient(Client):

    def __init__(self):
        api_credentials = django_backend.DjangoSettingsApiCredentialsBackend(self)
        super(DjangoClient, self).__init__(api_credentials)
