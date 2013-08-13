import json
import functools

from django import http
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from generic_request_signer.check_signature import check_signature

from request_signer import constants, models


def signature_required(func):
    """
    Decorator to require a signed request.

    :param func:
        The view function that requires a signature.

    :returns:
        A new view function wrapped to ensure it is properly signed.
    """

    @csrf_exempt
    @functools.wraps(func)
    def _wrap(request, *args, **kwargs):
        """
        Returns bad request when:
          - no signature
          - no client
          - signature doesnt match
        """
        if has_valid_signature(request) or allow_unsigned_requests():
            return func(request, *args, **kwargs)
        else:
            return http.HttpResponseBadRequest()

    _wrap.signature_required = True
    return _wrap


def allow_unsigned_requests():
    return getattr(settings, 'ALLOW_UNSIGNED_REQUESTS', False)


def has_valid_signature(request):
    signature = request.GET.get(constants.SIGNATURE_PARAM_NAME)
    client_id = request.GET.get(constants.CLIENT_ID_PARAM_NAME)

    if not signature or not client_id:
        return False

    client = models.AuthorizedClient.get_by_client(client_id)
    if client:
        url_path = request.get_full_path()
        request_data = get_request_data(request)
        return check_signature(signature, client.private_key, url_path, request_data)


def get_request_data(request):
    if request.META.get('CONTENT_TYPE') == 'application/json':
        request_data = json.loads(request.raw_post_data)
    else:
        request_data = dict(request.POST) or None
    return request_data
