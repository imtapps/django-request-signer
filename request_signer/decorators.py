
import functools

import apysigner

from django import http
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
import re

from request_signer import  constants, models


def check_signature(signature, private_key, full_path, payload):
    """
    Checks signature received and verifies that we are able to re-create
    it from the private key, path, and payload given.

    :param signature:
        Signature received from request.
    :param private_key:
        Base 64, url encoded private key.
    :full_path:
        Full path of request, including GET query string
    :payload:
        The request.POST data if present. None if not.

    :returns:
        Boolean of whether signature matched or not.
    """
    url_to_check = _strip_signature_from_url(signature, full_path)
    computed_signature = apysigner.get_signature(private_key, url_to_check, payload)
    return constant_time_compare(signature, computed_signature)

def _strip_signature_from_url(signature, url_path):
    """
    Strips signature off path. Can show up either as the first parameter
    or as an additional parameter (leading '?' or '&')
    """
    signature_qs = r"(\?|&)?{0}={1}$".format(constants.SIGNATURE_PARAM_NAME, signature)
    clean_url = re.sub(signature_qs, '', url_path, count=1)
    return clean_url


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
        signature = request.GET.get(constants.SIGNATURE_PARAM_NAME)
        client_id = request.GET.get(constants.CLIENT_ID_PARAM_NAME)

        if not signature or not client_id:
            return http.HttpResponseBadRequest()

        signature_valid = False
        client = models.AuthorizedClient.get_by_client(client_id)
        if client:
            url_path = request.get_full_path()
            post_data = request.POST or None
            signature_valid = check_signature(signature, client.private_key, url_path, post_data)

        if signature_valid:
            return func(request, *args, **kwargs)
        else:
            return http.HttpResponseBadRequest()

    _wrap.signature_required = True
    return _wrap
