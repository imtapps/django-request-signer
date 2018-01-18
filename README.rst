.. _django_request_signer:

Version 5 is compatible with Python 3 and Django 1.8+

*********************
Django Request Signer
*********************

Version 5 removes the AuthorizedClients model and does not look there for client ids or private keys.

Client ids and private keys must be in API_KEYS in settings.

```
API_KEYS = {'client_id_X': 'private_key_X'}
```

No data are removed or tables dropped. You can make the migrations that will do such.
