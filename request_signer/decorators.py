
import functools

from django import http
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt

from request_signer import  constants, models
from request_signer.signer import SignatureMaker

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
        signature_valid = False

        signature = request.GET.get(constants.SIGNATURE_PARAM_NAME)
        client_id = request.GET.get(constants.CLIENT_ID_PARAM_NAME)

        if not signature or not client_id:
            return http.HttpResponseBadRequest()

        client = models.AuthorizedClient.get_by_client(client_id)
        if client:
            computed_signature = SignatureMaker.get_signature(client.private_key, request.get_full_path(), request.POST or None)
            signature_valid = constant_time_compare(signature, computed_signature)

        if signature_valid:
            return func(request, *args, **kwargs)
        else:
            return http.HttpResponseBadRequest()

    _wrap.signature_required = True
    return _wrap
