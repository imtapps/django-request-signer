
from collections import defaultdict
import urllib
import urlparse
import hmac
import base64
import hashlib
import functools
from django import http
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt

from request_signer import models, constants

def is_list(v):
    return isinstance(v, (list, tuple))

def sort_vals(vals):
    return sorted(vals) if is_list(vals) else vals

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
            computed_signature = AuthSigner.get_signature(client.private_key, request.get_full_path(), request.POST or None)
            signature_valid = constant_time_compare(signature, computed_signature)

        if signature_valid:
            return func(request, *args, **kwargs)
        else:
            return http.HttpResponseBadRequest()

    return _wrap


class AuthSigner(object):
    """
    Creates an HMAC signature for a url and possible POST data payload.

    USAGE:
        signer = AuthSigner(<private_key>)
        signature = signer.create_signature('http://www.google.com?q=hmac+security')
    """
    private_key = None

    def __init__(self, private_key):
        self.private_key = private_key

        if self.private_key is None:
            raise Exception('Private key is required.')

    @classmethod
    def get_signature(cls, private_key, base_url, payload=None):
        return cls(private_key).create_signature(base_url, payload)

    def create_signature(self, base_url, payload=None):
        """
        Creates unique signature for request.

        :param base_url:
            The url you'll be using for urllib2.open
        :param payload:
            The POST data that you'll be sending. This must contain
            ALL the post data to be sent or the receiver won't be able
            to re-create the signature.
        """
        url = urlparse.urlparse(base_url)

        url_to_sign = url.path + '?' + self.get_signature_querystring(url)
        encoded_payload = self.get_signature_payload(payload)

        decoded_key = base64.urlsafe_b64decode(self.private_key.encode('utf-8'))
        signature = hmac.new(decoded_key, url_to_sign + encoded_payload, hashlib.sha256)
        return base64.urlsafe_b64encode(signature.digest())

    def get_signature_payload(self, payload):
        our_payload = dict(payload) if payload else {}
        self.remove_signature(our_payload)
        encoded_payload = self._encode_payload(our_payload)
        return encoded_payload

    def get_signature_querystring(self, url):
        tmp = urlparse.parse_qs(url.query)
        self.remove_signature(tmp)
        querystring = urllib.urlencode(tmp, True)
        return querystring

    def remove_signature(self, our_payload):
        if constants.SIGNATURE_PARAM_NAME in our_payload:
            del our_payload[constants.SIGNATURE_PARAM_NAME]

    def _encode_payload(self, payload):
        """
        Ensures the order of items coming from urlencode are the same
        every time so we can reliably recreate the signature.

        :param payload:
            The data to be sent in a GET or POST request.
            Can be a dictionary or it can be an iterable of
            two items, first being key, second being value(s).
        """
        if payload is None:
            return ''

        if hasattr(payload, 'items'):
            payload = payload.items()

        p = defaultdict(list)
        for k, v in payload:
            p[k].extend(v) if is_list(v) else p[k].append(v)
        ordered_params = [(k, sort_vals(p[k])) for k in sorted(p.keys())]

        return urllib.urlencode(ordered_params, True)
