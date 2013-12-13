from request_signer.client.generic import Client, WebException, django_backend


class BaseDjangoRestClient(Client):
    """
    Base Client for working with an api server using djangorestframework.

    Assumes your url structure of the api is the following:
      /api/endpoint/<item_list_key>/
      /api/endpoint/<item_list_key>/<item_detail_key>/

      Example:
      /api/endpoint/<company>/             # returns list of items for the company
      /api/endpoint/<company>/<service>/   # returns single item for company


    Django doesn't handle post data properly when the request is a "PUT", or
    anything other than "POST" really. So, for anything other than a GET or POST
    we need to add a "_method=PUT" or equivalent, which is how the django rest framework
    gets around this issue, but still uses full rest methods.
    """

    def __init__(self, api_credentials=None):
        api_credentials = api_credentials or django_backend.DjangoSettingsApiCredentialsBackend(self)
        super(BaseDjangoRestClient, self).__init__(api_credentials)

    BASE_API_ENDPOINT = None

    def build_endpoint(self, group_key, item_key=None):
        endpoint = "{base}{group_key}/".format(base=self.BASE_API_ENDPOINT, group_key=group_key)
        if item_key:
            endpoint += "{item_key}/".format(item_key=item_key)
        return endpoint

    def _get_json_response(self, http_method, endpoint, data=None):
        headers = {"Accept": "application/json"}
        return self._get_response(http_method, endpoint, data, headers=headers)

    def get_list(self, group_key):
        """
        :param group_key:
            The key to the group of items desired (eg. company_id)

        :returns:
            Returns list of items returned.
            When client returns a 404 returned from the client,
            an empty list is returned instead of an exception
        """
        endpoint = self.build_endpoint(group_key)
        r = self._get_json_response("GET", endpoint)
        if not r.is_successful and r.status_code != 404:
            raise WebException(r.read())
        return r.json

    def get_item(self, group_key, item_key):
        """
        :param group_key:
            The key to the group of items desired (eg. company_id)
        :param item_key:
            The key to the item desired

        :returns:
            Returns dictionary representation of item.
        """
        endpoint = self.build_endpoint(group_key, item_key)
        r = self._get_json_response("GET", endpoint)
        if not r.is_successful and r.status_code != 404:
            raise WebException(r.read())
        return r.json

    def create(self, group_key, **attrs):
        """
        :param group_key:
            The key to the group of items desired (eg. company_id)
        :param attrs:
            Attributes used to create the item.
            Note: the keys of "group key" and "item key" will need to be include
                  in the attrs or the item won't get built properly.
        :returns:
            JSON representation of item on success, raises exception on error
        """
        endpoint = self.build_endpoint(group_key)
        r = self._get_json_response("POST", endpoint, data=attrs)
        if not r.is_successful:
            raise WebException(r.read())
        return r.json

    def update(self, group_key, item_key, **attrs):
        """
        :param group_key:
            The key to the group of items desired (eg. company_id)
        :param item_key:
            The key to the item desired
        :param attrs:
            Attributes used to create the item.
            Note: the keys of "group key" and "item key" will need to be include
                  in the attrs or the item won't get built properly.
        :returns:
            JSON representation of item on success, raises exception on error
        """
        endpoint = self.build_endpoint(group_key, item_key)
        attrs["_method"] = "PUT"
        r = self._get_json_response("POST", endpoint, data=attrs)
        if not r.is_successful:
            raise WebException(r.read())
        return r.json

    def delete(self, group_key, item_key):
        """
        :param group_key:
            The key to the group of items desired (eg. company_id)
        :param item_key:
            The key to the item desired
        :returns:
            JSON response on success (should be empty dict)
            raises exception on error, but 404 means resource doesn't
            exist so there is nothing to delete and we let it slide.
        """
        endpoint = self.build_endpoint(group_key, item_key)
        attrs = {"_method": "DELETE"}
        r = self._get_json_response("POST", endpoint, data=attrs)
        if not r.is_successful and r.status_code != 404:
            raise WebException(r.read())
        return r.json
