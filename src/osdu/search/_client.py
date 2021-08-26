# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Search client for working with the OSDU search API."""

from typing import Union
from osdu.client import OsduClient


# pylint: disable=too-few-public-methods
class SearchClient():
    # Dev. notes:
    # inspiration from:
    # https://github.com/Azure/azure-sdk-for-python/blob/3fe8964c8831c9ce91c4a4bc0dadcbc525b74220/sdk/keyvault/azure-keyvault-keys/azure/keyvault/keys/_client.py
    # https://github.com/Azure/azure-sdk-for-python/blob/3fe8964c8831c9ce91c4a4bc0dadcbc525b74220/sdk/keyvault/azure-keyvault-certificates/azure/keyvault/certificates/_shared/client_base.py#L34
    # TO DO Model, or string / dict based API calls!
    # TO DO Async v non async calls
    # TO DO Cursor / paging support.
    """A client for working with the OSDU Search API.
    """

    # versions of the api that we currently support.
    valid_versions = [2]

    @property
    def version(self):
        """Version of the api being used

        Returns:
            int: Version of the api being used
        """
        return self._version

    def __init__(self,
                 client: OsduClient,
                 service_version: Union[int, str] = 'latest'):
        """Setup the SearchClient

        Args:
            client (OsduClient): client to use for connection
            service_version (Union[int, str], optional): service version (3 or 'latest') Defaults to 'latest'.

        Raises:
            ValueError: [description]
        """

        if not client or not isinstance(client, OsduClient):
            raise ValueError("client should be an OsduClient instance")

        if service_version not in self.valid_versions and service_version != 'latest':
            raise ValueError(
                f"This package doesn't support API version '{service_version}'.\n"
                + f"Supported versions: {', '.join(str(v) for v in self.valid_versions)} or 'latest'")

        self._client = client
        self._version = self.valid_versions[-1] if service_version == 'latest' else service_version

    def api_url(self, extra_path: str = None):
        """Get a url for the api including any specified extra path

        Args:
            extra_path (str, optional): extra path to add to the base url. Defaults to None.

        Returns:
            str: api url
        """
        url = self._client.server_url.rstrip('/') + f"/api/search/v{self.version}/"
        if extra_path is not None:
            url = url + extra_path
        return url

    # def query():
    #     pass

    # def query_by_id():
    #     pass

    def is_healthy(self) -> bool:
        """Returns health status of the API

        Returns:
            bool: health status of the API
        """
        response = self._client.get(self.api_url('health/readiness_check'))
        return response.status_code == 200

    def query_all_aggregated(self) -> dict:
        """Returns a list of all kinds including number of records

        Returns:
            dict: containing the result
        """
        request_data = {
            "kind": "*:*:*:*",
            "limit": 1,
            "query": "*",
            "aggregateBy": "kind"
        }
        response_json = self._client.post_returning_json(self.api_url('query'), request_data)
        return response_json
