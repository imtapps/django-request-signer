from request_signer.client.generic.base import BasicSettingsApiCredentialsBackend

__all__ = ('FlaskSettingsApiCredentialsBackend')


class FlaskSettingsApiCredentialsBackend(BasicSettingsApiCredentialsBackend):

    def __init__(self, client, config):
        self.config = config
        super(FlaskSettingsApiCredentialsBackend, self).__init__(client)

    def get_setting(self, name):
        client_name = self.get_client_name(name)
        setting = self.config.get(client_name, None)
        if not setting:
            raise Exception(self.CLIENT_ERROR_MESSAGE.format(name))
        return setting

    def get_client_name(self, name):
        client_name = getattr(self.client, name, None)
        if not client_name:
            raise Exception(self.CLIENT_ERROR_MESSAGE.format(name))
        return client_name
