
import base64
import hashlib
import hmac
import random
import time

from django.db import models


def create_private_key():
    """
    Creates new private key to be used for signing requests.

    :returns:
        base64_urlsafe private key
    """
    msg = "{0}{1}".format(time.time(), random.random())
    s = hmac.new("request-signer", msg, hashlib.sha256)
    return base64.urlsafe_b64encode(s.digest())


class AuthorizedClient(models.Model):
    client_id = models.CharField(max_length=20, primary_key=True)
    private_key = models.CharField(max_length=100, default=create_private_key)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        app_label = 'request_signer'

    @classmethod
    def get_by_client(cls, client_id):
        try:
            return cls.objects.get(pk=client_id, is_active=True)
        except cls.DoesNotExist:
            return None


class AuthorizedServiceProvider(models.Model):
    base_url = models.URLField(primary_key=True)
    client_id = models.CharField(max_length=20)
    private_key = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True
