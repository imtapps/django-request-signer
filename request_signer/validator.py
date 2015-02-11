
from django.http import QueryDict
from django.utils.functional import cached_property
from generic_request_signer.check_signature import check_signature

from request_signer import constants, models
from request_signer.signals import successful_signed_request


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
            return check_signature(self.signature, self.client.private_key, self.url_path, self.request_data)

    @property
    def signature(self):
        return self.request.GET.get(constants.SIGNATURE_PARAM_NAME)

    @property
    def client_id(self):
        return self.request.GET.get(constants.CLIENT_ID_PARAM_NAME)

    @property
    def url_path(self):
        return self.request.get_full_path()

    @property
    def client(self):
        if not self.signature or not self.client_id:
            return False

        return models.AuthorizedClient.get_by_client(self.client_id)

    @property
    def request_data(self):
        if self.request.META.get('CONTENT_TYPE') == 'application/json':
            request_data = self.request.body
        elif self.request.method.lower() == 'patch':
            request_data = QueryDict(self.request.body, encoding='utf-8')
        else:
            request_data = dict(self.request.POST) or None
        return request_data
