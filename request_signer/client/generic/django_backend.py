from request_signer.client.generic.base import BasicSettingsApiCredentialsBackend

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class DjangoSettingsApiCredentialsBackend(BasicSettingsApiCredentialsBackend):

    def get_setting(self, name):
        client_name = self.get_client_name(name)
        setting = getattr(settings, client_name, None)
        if not setting:
            raise ImproperlyConfigured(self.CLIENT_SETTINGS_ERROR_MESSAGE.format(client_name))
        return setting

    def get_client_name(self, name):
        client_name = getattr(self.client, name, None)
        if not client_name:
            raise ImproperlyConfigured(self.CLIENT_ERROR_MESSAGE.format(name))
        return client_name
