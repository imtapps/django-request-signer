import mock
import unittest
from request_signer.client.generic.base import BasicSettingsApiCredentialsBackend
from request_signer.client.generic.flask_backend import FlaskSettingsApiCredentialsBackend


class FlaskClient(object):
    domain_settings_name = 'APPS_AUTH_CLIENT_DOMAIN'
    client_id_settings_name = 'APPS_AUTH_CLIENT_ID'
    private_key_settings_name = 'APPS_AUTH_PRIVATE_KEY'


class FlaskSettingsApiCredentialsBackendTests(unittest.TestCase):

    sut_class = FlaskSettingsApiCredentialsBackend

    def setUp(self):
        self.client = FlaskClient()
        self.config = dict(
            APPS_AUTH_CLIENT_DOMAIN="http://www.sample.com",
            APPS_AUTH_CLIENT_ID="SAMPLECLIENTID",
            APPS_AUTH_PRIVATE_KEY="Q0TBXqjE60nfoHaQ1CZxWxt4JBUyhBPJkH1y_274tDI="
        )

    def test_is_subclass_of_the_basic_settings_backend(self):
        self.assertTrue(issubclass(self.sut_class, BasicSettingsApiCredentialsBackend))

    def test_is_captures_required_configuration_during_init(self):
        with mock.patch.object(BasicSettingsApiCredentialsBackend, '__init__'):
            sut = self.sut_class(self.client, self.config)
        self.assertEqual(sut.config, self.config)

    def test_invokes_super_with_client(self):
        with mock.patch.object(BasicSettingsApiCredentialsBackend, '__init__') as init:
            self.sut_class(self.client, self.config)
        init.assert_called_once_with(self.client)

    def test_get_domain_settings_name_returns_value_when_available(self):
        sut = self.sut_class(self.client, self.config)
        setting = sut.get_setting('domain_settings_name')
        self.assertEqual(setting, 'http://www.sample.com')

    def test_get_domain_settings_name_raises_exception_when_setting_not_available(self):
        sut = self.sut_class(self.client, {})
        with self.assertRaises(Exception) as ex:
            sut.get_setting('domain_settings_name')
        self.assertEqual(ex.exception.message, "Client implementations must define a `domain_settings_name` attribute")

    def test_get_client_id_settings_name_returns_value_when_available(self):
        sut = self.sut_class(self.client, self.config)
        setting = sut.get_setting('client_id_settings_name')
        self.assertEqual(setting, 'SAMPLECLIENTID')

    def test_get_client_id_settings_name_raises_exception_when_setting_not_available(self):
        sut = self.sut_class(self.client, {})
        with self.assertRaises(Exception) as ex:
            sut.get_setting('client_id_settings_name')
        self.assertEqual(ex.exception.message, "Client implementations must define a `client_id_settings_name` attribute")

    def test_get_private_key_settings_name_returns_value_when_available(self):
        sut = self.sut_class(self.client, self.config)
        setting = sut.get_setting('private_key_settings_name')
        self.assertEqual(setting, 'Q0TBXqjE60nfoHaQ1CZxWxt4JBUyhBPJkH1y_274tDI=')

    def test_get_private_key_settings_name_raises_exception_when_setting_not_available(self):
        sut = self.sut_class(self.client, {})
        with self.assertRaises(Exception) as ex:
            sut.get_setting('private_key_settings_name')
        self.assertEqual(ex.exception.message, "Client implementations must define a `private_key_settings_name` attribute")
