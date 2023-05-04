# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Base client for authentication and communicating with OSDU."""

import logging

from .base import OsduBaseCredential
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)


class OsduMsalNonInteractiveCredential(OsduBaseCredential):
    """Get token based client for connecting with OSDU."""

    @property
    def client_id(self) -> str:
        """Client id used for authorisation

        Returns:
            str: client id
        """
        return self._client_id

    @property
    def client_secret(self) -> str:
        """Client secret used for authorisation

        Returns:
            str: client secret
        """
        return self._client_secret

    @property
    def authority(self) -> str:
        """Authority url for obtaining token

        Returns:
            str: authority url
        """
        return self._authority

    @property
    def scopes(self) -> str:
        """The current scopes requested

        Returns:
            str: scopes
        """
        return self._scopes

    @property
    def msal_confidential_client(self) -> object:
        """The current scopes requested

        Returns:
            ConfidentialClientApplication: object
        """
        return self._msal_confidential_client

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 authority: str,
                 scopes: str,
                 client: ConfidentialClientApplication):
        """Setup the new client

        Args:
            client_id (str): client id for connecting
            authority (str): authority url
            scopes (str): scopes to request
        """
        super().__init__()
        self._msal_confidential_client = client
        self._client_id = client_id
        self._client_secret = client_secret
        self._authority = authority
        self._scopes = scopes

    def get_token(self, **kwargs) -> str:
        """
        return access_token.
        """
        token = self._get_token()
        if 'access_token' in token:
            return token['access_token']

    def _get_token(self) -> dict:
        """Get token using msal confidential client.

         Returns:
            dict: Dictionary representing the returned token
        """
        result = self._msal_confidential_client.acquire_token_silent([self._scopes], account=None)
        if result:
            return result
        return self._msal_confidential_client.acquire_token_for_client([self._scopes])
