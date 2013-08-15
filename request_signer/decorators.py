import functools

from django import http
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from request_signer import validator


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


def get_validator(request):
    return validator.SignatureValidator(request)


def has_valid_signature(request):
    return get_validator(request).has_valid_signature()
