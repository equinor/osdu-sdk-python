# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Search client for working with the OSDU search API."""

from typing import Union

from osdu.client import OsduClient
from osdu.serviceclientbase import ServiceClientBase

VALID_SEARCH_API_VERSIONS = [2]


# pylint: disable=too-few-public-methods
class SearchClient(ServiceClientBase):
    # Dev. notes:
    # inspiration from:
    # https://github.com/Azure/azure-sdk-for-python/blob/3fe8964c8831c9ce91c4a4bc0dadcbc525b74220/sdk/keyvault/azure-keyvault-keys/azure/keyvault/keys/_client.py
    # https://github.com/Azure/azure-sdk-for-python/blob/3fe8964c8831c9ce91c4a4bc0dadcbc525b74220/sdk/keyvault/azure-keyvault-certificates/azure/keyvault/certificates/_shared/client_base.py#L34
    # TO DO Model, or string / dict based API calls!
    # TO DO Async v non async calls
    # TO DO Cursor / paging support.
    """A client for working with the OSDU Search API."""

    def __init__(self, client: OsduClient, service_version: Union[int, str] = "latest"):
        """Setup the SearchClient

        Args:
            client (OsduClient): client to use for connection
            service_version (Union[int, str], optional): service version (3 or 'latest') Defaults to 'latest'.

        Raises:
            ValueError: [description]
        """
        super().__init__(client, "search", VALID_SEARCH_API_VERSIONS, service_version)

    # def query():
    #     pass

    # def query_by_id():
    #     pass

    def is_healthy(self) -> bool:
        """Returns health status of the API

        Returns:
            bool: health status of the API
        """
        response = self._client.get(self.api_url("health/readiness_check"))
        return response.status_code == 200

    def query_all_aggregated(self) -> dict:
        """Returns a list of all kinds including number of records

        Returns:
            dict: containing the result
        """
        request_data = {"kind": "*:*:*:*", "limit": 1, "query": "*", "aggregateBy": "kind"}
        response_json = self._client.post_returning_json(self.api_url("query"), request_data)
        return response_json

    def query(
        self, kind: str = None, identifier: str = None, query: str = None, limit: int = None
    ) -> dict:
        """Query records

        Args:
            kind (str): kind to query for
            identifier (str): id to query for
            query (str): a specific query
            limit (str): limit on number of records to return

        Returns:
            dict: containing the result
        """

        if identifier is not None and query is not None:
            raise ValueError("You can't specify both identifier and query")

        request_data = {}
        if kind is None:
            request_data["kind"] = "*:*:*:*"
        else:
            request_data["kind"] = kind

        if identifier is not None:
            request_data["query"] = f'id:("{identifier}")'

        if query is not None:
            request_data["query"] = query

        if limit is not None:
            request_data["limit"] = limit

        response_json = self._client.post_returning_json(self.api_url("query"), request_data)
        return response_json

    def query_by_id(self, identifier: str, limit: int = None) -> dict:
        """Returns a list of all kinds including number of records

        Args:
            identifier (str): id to query for

        Returns:
            dict: containing the result
        """
        request_data = {
            "kind": "*:*:*:*",
            "query": f'id:("{identifier}")',
        }

        if limit is not None:
            request_data["limit"] = limit

        response_json = self._client.post_returning_json(self.api_url("query"), request_data)
        return response_json

    def query_by_kind(self, kind: str, limit: int = None) -> dict:
        """Returns a list of all records for the given kind

        Args:
            kind (str): kind to query for

        Returns:
            dict: containing the result
        """
        request_data = {"kind": kind}

        if limit is not None:
            request_data["limit"] = limit

        response_json = self._client.post_returning_json(self.api_url("query"), request_data)
        return response_json
