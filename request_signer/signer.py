
import base64
from collections import defaultdict
import hashlib
import hmac
import urllib
import urlparse

from request_signer import constants

__all__ = (
    'SignatureMaker',
)

def is_list(v):
    return isinstance(v, (list, tuple))

def sort_vals(vals):
    return sorted(vals) if is_list(vals) else vals



class SignatureMaker(object):
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

        url_to_sign = url.path + '?' + self._get_signature_querystring(url)
        encoded_payload = self._encode_payload(payload)

        decoded_key = base64.urlsafe_b64decode(self.private_key.encode('utf-8'))
        signature = hmac.new(decoded_key, url_to_sign + encoded_payload, hashlib.sha256)
        return base64.urlsafe_b64encode(signature.digest())

    def _get_signature_querystring(self, url):
        tmp = urlparse.parse_qs(url.query)
        self._remove_signature(tmp)
        return urllib.urlencode(tmp, True)

    def _remove_signature(self, our_payload):
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
