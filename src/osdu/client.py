# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Useful functions."""

import logging
from typing import Union

import requests
from requests.models import HTTPError

from osdu.identity import OsduBaseCredential

logger = logging.getLogger(__name__)


class OsduClient:
    """
    Class for connecting with API's.
    """

    @property
    def server_url(self) -> str:
        """Url of the API server

        Returns:
            str: api server url
        """
        return self._server_url

    @property
    def data_partition(self) -> str:
        """Name of the data partition

        Returns:
            str: data partition name
        """
        return self._data_partition

    @property
    def credentials(self) -> str:
        """Credentials used for connection

        Returns:
            OsduBaseCredential: credentials
        """
        return self._credentials

    @property
    def retries(self) -> int:
        """Number of retries incase of http errors

        Returns:
            int: number of retries incase of http errors
        """
        return self._retries

    def __init__(
        self,
        server_url: str,
        data_partition: str,
        credentials: OsduBaseCredential,
        retries: int = 0,
    ):
        """Setup the new client

        Args:
            server_url (str): url of the server without any path e.g. https://www.test.com
            data_partition (str): data partition name e.g. opendes
            credentials (OsduBaseCredential): credentials used for connection
            retries (int): number of retries incase of http errors (default 0 - no retries)
        """
        self._server_url = server_url
        self._data_partition = data_partition
        self._credentials = credentials
        self._retries = retries

    def get_headers(self):
        """Get needed http headers, including authorization bearer token.

        Raises:
            NotImplementedError: Should be implemented by subclasses.
        """
        return {
            "Content-Type": "application/json",
            "data-partition-id": self.data_partition,
            "Authorization": f"Bearer {self.credentials.get_token()}",
        }

    # region HTTP methods
    def get(self, url: str) -> requests.Response:
        """GET from the specified url

        Args:
            url (str): url to GET from to

        Returns:
            requests.Response: response object
        """
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response

    def get_returning_json(self, url: str, ok_status_codes: list = None) -> dict:
        """Get data from the specified url in json format.

        Args:
            url (str): url to GET from to
            ok_status_codes (list, optional): Status codes for successful call. Defaults to [200].

        Raises:
            HTTPError: Raised if the get returns a status other than those in ok_status_codes

        Returns:
            dict: response json
        """
        if ok_status_codes is None:
            ok_status_codes = [200]
        response = self.get(url)
        if response.status_code not in ok_status_codes:
            raise HTTPError(response=response)
        return response.json()

    def post(self, url: str, data: Union[str, dict]) -> requests.Response:
        """POST data to the specified url

        Args:
            url (str): url to POST to
            data (Union[str, dict]): json data as string or dict to send as the body

        Returns:
            [requests.Response]: response object
        """
        headers = self.get_headers()
        # logger.debug(url)
        # logger.debug(data)

        # determine whether to send to requests as data or json
        _json = None
        if isinstance(data, dict):
            _json = data
            data = None

        response = requests.post(url, data=data, json=_json, headers=headers)
        # logger.debug(response.text)
        return response

    def post_returning_json(
        self, url: str, data: Union[str, dict], ok_status_codes: list = None
    ) -> dict:
        """Post data to the specified url and get the result in json format.

        Args:
            url (str): url to POST to
            data (Union[str, dict]): json data as string or dict to send as the body
            ok_status_codes (list, optional): Status codes indicating successful call. Defaults to [200].

        Raises:
            HTTPError: Raised if the get returns a status other than those in ok_status_codes

        Returns:
            dict: response json
        """
        if ok_status_codes is None:
            ok_status_codes = [200]
        response = self.post(url, data)
        if response.status_code not in ok_status_codes:
            raise HTTPError(response=response)
        return response.json()

    def put(self, url: str, filepath: str) -> requests.Response:
        """PUT from the file at the given path to a url

        Args:
            url (str): url to PUT to
            filepath (str): path to a file to PUT

        Returns:
            requests.Response: response object
        """
        headers = self.get_headers()
        headers.update({"Content-Type": "application/octet-stream", "x-ms-blob-type": "BlockBlob"})
        with open(filepath, "rb") as file_handle:
            response = requests.put(url, data=file_handle, headers=headers)
            return response

    def delete(self, url: str, ok_status_codes: list = None) -> requests.Response:
        """GET to a url

        Args:
            url (str): url to PUT to
            ok_status_codes (list, optional): Status codes indicating successful call. Defaults to [200].

        Returns:
            requests.Response: response object
        """
        if ok_status_codes is None:
            ok_status_codes = [200]

        headers = self.get_headers()
        response = requests.delete(url, headers=headers)

        if response.status_code not in ok_status_codes:
            raise HTTPError(response=response)

        return response

    # endregion HTTP Actions
