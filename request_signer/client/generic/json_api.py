from request_signer.client.generic import Client, WebException, django_backend


class BaseDjangoJsonApiClient(Client):

    EXCEPTION_TYPE = WebException

    def __init__(self, company, api_credentials=None):
        self.company = company
        api_credentials = api_credentials or django_backend.DjangoSettingsApiCredentialsBackend(self)
        super(BaseDjangoJsonApiClient, self).__init__(api_credentials)

    def get(self, resource, lookup_field=None):
        headers = {'Accept': 'application/vnd.api+json', 'company': self.company}
        return self.get_response('GET', resource, lookup_field, headers=headers)

    def update(self, resource, lookup_field, data=None):
        headers = {'Accept': 'application/vnd.api+json',
                   'Content-Type': 'application/vnd.api+json',
                   'company': self.company}
        return self.get_response('PATCH', resource, lookup_field, data, headers)

    def create(self, resource, data=None):
        headers = {'Accept': 'application/vnd.api+json',
                   'Content-Type': 'application/vnd.api+json',
                   'company': self.company}
        return self.get_response('POST', resource, data=data, headers=headers)

    def delete(self, resource, lookup_field):
        headers = {'Accept': 'application/vnd.api+json', 'company': self.company}
        return self.get_response('DELETE', resource, lookup_field, headers=headers)

    def get_response(self, method, resource, lookup_field=None, data=None, headers=None):
        endpoint = '/{}/'.format(resource)
        if lookup_field:
            endpoint += '{}/'.format(lookup_field)
        response = self._get_response(method, endpoint, data, headers=headers)
        if not response.is_successful and response.status_code != 404:
            raise self.EXCEPTION_TYPE(response.read())
        return response
