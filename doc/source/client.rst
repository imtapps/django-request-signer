
*********************
Request Signer Client
*********************

Creating a signed request
=========================

You can create a signed URL using the SignedRequestFactory's build_request_url method::

    from request_signer.client.generic import SignedRequestFactory

    factory = SignedRequestFactory('http_method', 'client_id', 'private_key')
    signed_request_url = factory.build_request_url(post_data_dict_or_none, 'request_url')

Alternatively, you can create a client class to encapsulate dealing with external services::

    from request_signer.client.generic import Client

    class OurClient(Client):
        domain_settings_name = 'DJANGO_SETTINGS_SERVICE_DOMAIN'
        client_id_settings_name = 'DJANGO_SETTINGS_CLIENT_ID'
        private_key_settings_name = 'DJANGO_SETTINGS_PRIVATE_KEY'

        def do_some_remote_action(self, whatever, args, you, want):
            response = self._get_response('POST', '/service/endpoint/',
                dict(arg1=whatever, arg2=you, arg3=want))
            return response.is_successful

        def get_some_remote_data(self, key):
            response = self._get_response('GET', '/service/endpoint/{key}'.format(key=key))
            return response.json

To use this client class::

    client = OurClient()
    if client.do_some_remote_action("this", "thing", "rocks", "hard"):
        server_json = client.get_some_remote_data(123)
        print server_json['secret']
    else:
        print "fail!"

