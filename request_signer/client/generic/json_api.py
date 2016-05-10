from request_signer.client.generic import Client, WebException, django_backend


class BaseDjangoJsonApiClient(Client):

    def __init__(self, api_credentials=None, exception_type=WebException):
        api_credentials = api_credentials or django_backend.DjangoSettingsApiCredentialsBackend(self)
        self.exception_type = exception_type
        super(BaseDjangoJsonApiClient, self).__init__(api_credentials)

    def get(self, resource, lookup_field=None):
        endpoint = '/{}/'.format(resource)
        if lookup_field:
            endpoint += '{}/'.format(lookup_field)
        response = self._get_response('GET', endpoint, None, headers={'Accept': 'application/vnd.api+json'})
        if self.request_unsuccessful(response):
            raise self.exception_type(response.read())
        return response

    def update(self, resource, lookup_field, data=None):
        endpoint = '/{}/{}/'.format(resource, lookup_field)
        response = self._get_response(
            'PATCH',
            endpoint,
            data,
            headers={
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'
            }
        )
        if self.request_unsuccessful(response):
            raise self.exception_type(response.read())
        return response

    def create(self, resource, data=None):
        endpoint = '/{}/'.format(resource)
        response = self._get_response(
            'POST',
            endpoint,
            data,
            headers={
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json'
            }
        )
        if self.request_unsuccessful(response):
            raise self.exception_type(response.read())
        return response

    def delete(self, resource, lookup_field):
        endpoint = '/{}/{}/'.format(resource, lookup_field)
        response = self._get_response('DELETE', endpoint, headers={'Accept': 'application/vnd.api+json'})
        if self.request_unsuccessful(response):
            raise self.exception_type(response.read())
        return response

    def request_unsuccessful(self, response):
        return not response.is_successful and response.status_code != 404
