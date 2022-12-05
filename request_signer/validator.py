import six
from collections import namedtuple
from django.conf import settings
from django.http import QueryDict
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from generic_request_signer.check_signature import check_signature

from request_signer import constants
from request_signer.signals import successful_signed_request

if six.PY3:
    from urllib.parse import unquote
else:
    from urllib import unquote


class SignatureValidator(object):

    def __init__(self, request):
        self.request = request

    def has_valid_signature(self):
        self._fire_signal_when_signature_valid()
        return self.signature_was_valid

    def _fire_signal_when_signature_valid(self):
        if self.signature_was_valid:
            successful_signed_request.send(sender=self, request=self.request)

    @cached_property
    def signature_was_valid(self):
        if self.client:
            result = check_signature(self.signature, self.client.private_key, self.url_path, self.request_data)
            return result or check_signature(
                self.signature, self.client.private_key, unquote(self.url_path), self.request_data
            ) or self.unquote_base_url

    @property
    def unquote_base_url(self):
        url, query = self.url_path.split('?')
        return check_signature(
            self.signature, self.client.private_key, '{}?{}'.format(unquote(url), query), self.request_data
        )

    @property
    def signature(self):
        return self.request.GET.get(constants.SIGNATURE_PARAM_NAME)

    @property
    def client_id(self):
        return self.request.GET.get(constants.CLIENT_ID_PARAM_NAME)

    @property
    def url_path(self):
        return self.request.get_full_path()

    @cached_property
    def client(self):
        if not self.signature or not self.client_id:
            return False
        if getattr(settings, 'API_KEYS', None):
            Client = namedtuple('client', ['private_key'])
            return Client(settings.API_KEYS.get(self.client_id, ''))
        raise ImproperlyConfigured('API_KEYS not found in settings')

    @property
    def request_data(self):
        if self.request.META.get('CONTENT_TYPE') in ['application/json', 'application/vnd.api+json']:
            request_data = self.request.body
        elif self.request.method.lower() in ['patch', 'put']:
            request_data = dict(QueryDict(self.request.body, encoding='utf-8'))
        else:
            request_data = dict(self.request.POST)
        return request_data
