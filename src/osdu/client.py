# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Useful functions."""

import json
import logging
from typing import Tuple

import requests

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

    def __init__(self,
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
        # send batch request for creating records
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response

    def get_returning_json(self, url: str) -> Tuple[requests.Response, dict]:
        """Get data from the specified url in json format.

        Args:
            url (str): url to GET from to

        Returns:
            dict: response json
        """
        response = self.get(url)
        return response, response.json()

    def post(self, url: str, data: str) -> requests.Response:
        """POST data to the specified url

        Args:
            url (str): url to POST to
            data (str): data to send as the body

        Returns:
            [requests.Response]: response object
        """
        headers = self.get_headers()
        # logger.debug(url)
        # logger.debug(data)
        response = requests.post(url, data, headers=headers)
        # logger.debug(response.text)
        return response

    def post_json(self, url: str, json_data: dict) -> requests.Response:
        """POST json data to a url

        Args:
            url (str): url to POST to
            json_data (dict): json to send as the body

        Returns:
            requests.Response: response object
        """

        data = json.dumps(json_data)
        return self.post(url, data)

    def post_json_returning_json(self, url: str, json_data: dict) -> Tuple[requests.Response, dict]:
        """Post json data to the specified url and get the result in json format.

        Args:
            url (str): url to POST to
            json_data (dict): json to send as the body

        Returns:
            Tuple[requests.Response, dict]: response object, json
        """
        response = self.post_json(url, json_data)
        return response, response.json()

    def put(self, url: str, filepath: str) -> requests.Response:
        """PUT from the file at the given path to a url

        Args:
            url (str): url to PUT to
            filepath (str): path to a file to PUT

        Returns:
            requests.Response: response object
        """
        # send batch request for creating records
        headers = self.get_headers()
        headers.update({
            "Content-Type": "application/octet-stream",
            "x-ms-blob-type": "BlockBlob"
        })
        with open(filepath, 'rb') as file_handle:
            response = requests.put(url, data=file_handle, headers=headers)
            return response
    # endregion HTTP Actions
