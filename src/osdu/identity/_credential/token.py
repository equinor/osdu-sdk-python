# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Base client for authentication and communicating with OSDU."""

import logging
from datetime import datetime
from json import loads
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import OsduBaseCredential

logger = logging.getLogger(__name__)


class OsduTokenCredential(OsduBaseCredential):
    """Refresh token based client for connecting with OSDU."""

    __access_token_expire_date = 0
    __access_token = None
    # __id_token = None

    @property
    def client_id(self) -> str:
        """Client id used for authorisation

        Returns:
            str: client id
        """
        return self._client_id

    @property
    def token_endpoint(self) -> str:
        """Token endpoint for refreshing token

        Returns:
            str: token endpoint
        """
        return self._token_endpoint

    @property
    def refresh_token(self) -> str:
        """The current refresh token

        Returns:
            str: refresh token
        """
        return self._refresh_token

    @property
    def client_secret(self) -> str:
        """The currently used client secret

        Returns:
            str: client secret
        """
        return self._client_secret

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        client_id: str,
        token_endpoint: str,
        refresh_token: str,
        client_secret: str,
    ):
        """Setup the new client

        Args:
            client_id (str): client id for connecting
            token_endpoint (str): token endpoint for refreshing token
            refresh_token (str): refresh token
            client_secret (str): client secret
        """
        super().__init__()
        self._client_id = client_id
        self._token_endpoint = token_endpoint
        self._refresh_token = refresh_token
        self._client_secret = client_secret

    def get_token(self, **kwargs) -> str:
        """
        Check expiration date and return access_token.
        """
        if datetime.now().timestamp() > self.__access_token_expire_date:
            self.refresh_access_token()
        return self.__access_token

    def _refresh_access_token(self) -> dict:
        """
        Send refresh token requests to OpenID token endpoint.

        Return dict with keys "access_token", "expires_in", "scope", "token_type", "id_token".
        """
        body = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = urlencode(body).encode("utf8")
        request = Request(url=self._token_endpoint, data=data, headers=headers)
        try:
            with urlopen(request) as response:
                response_body = response.read()
                return loads(response_body)
        except HTTPError as ex:
            code = ex.code
            message = ex.read().decode("utf8")
            logger.error("Refresh token request failed. %s %s", code, message)
            raise

    def refresh_access_token(self) -> dict:
        """Refresh from refresh token.

        Returns:
            dict: Dictionary representing the returned token
        """
        # for i in range(self.retries + 1):
        #     # try several times if there any error
        #     try:
        #         result = self._refresh_access_token()
        #         break
        #     except HTTPError:
        #         if i == self._retries - 1:
        #             # too many errors, raise original exception
        #             raise
        result = self._refresh_access_token()

        if "access_token" in result:
            # self.__id_token = result["id_token"]
            self.__access_token = result["access_token"]
            self.__access_token_expire_date = datetime.now().timestamp() + result["expires_in"]

            # logger.info("Token is refreshed.")
        else:
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("correlation_id"))

        return result  # You may need this when reporting a bug
