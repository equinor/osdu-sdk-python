# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Base client for authentication and communicating with OSDU."""

import logging
import os

from osdu.identity.consts import EnvironmentVariables
from osdu.identity.exceptions import CredentialUnavailableError

from .base import OsduBaseCredential
from .msal_interactive import OsduMsalInteractiveCredential
from .token import OsduTokenCredential

_logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class OsduEnvironmentCredential(OsduBaseCredential):
    """A credential configured by environment variables.

    This credential is capable of authenticating using a refresh token, or msal interactive.
    Configuration is attempted in this order, using these environment variables:
    Refresh token:
      - **CLIENT_ID**: client id for connecting
      - **TOKEN_ENDPOINT**: token endpoint for refreshing token
      - **REFRESH_TOKEN**: refresh token
      - **CLIENT_SECRET**: client secret
    Msal interactive:
      - **CLIENT_ID**: client id for connecting
      - **AUTHORITY**: authority url
      - **SCOPES**: scopes to request.
      - **TOKEN_CACHE**: (optional) Path to token cache.

    If a prefix is specified then this is prepended to the above names.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, prefix=None, **kwargs):
        """Setup the new credential based upon environment variables.

        Args:
            prefix (str): optional prefix for standard environment variable names
        """
        self._prefix = prefix
        self._credential = None

        if all(
            os.environ.get(self._expand_environment_name(v)) is not None
            for v in EnvironmentVariables.TOKEN_VARS
        ):
            self._credential = OsduTokenCredential(
                client_id=os.environ[self._expand_environment_name(EnvironmentVariables.CLIENT_ID)],
                token_endpoint=os.environ[
                    self._expand_environment_name(EnvironmentVariables.TOKEN_ENDPOINT)
                ],
                refresh_token=os.environ[
                    self._expand_environment_name(EnvironmentVariables.REFRESH_TOKEN)
                ],
                client_secret=os.environ[
                    self._expand_environment_name(EnvironmentVariables.CLIENT_SECRET)
                ],
                **kwargs,
            )
        elif all(
            os.environ.get(self._expand_environment_name(v)) is not None
            for v in EnvironmentVariables.MSAL_INTERACTIVE_VARS
        ):
            self._credential = OsduMsalInteractiveCredential(
                client_id=os.environ[self._expand_environment_name(EnvironmentVariables.CLIENT_ID)],
                authority=os.environ[self._expand_environment_name(EnvironmentVariables.AUTHORITY)],
                scopes=os.environ[self._expand_environment_name(EnvironmentVariables.SCOPES)],
                token_cache=os.environ.get(
                    self._expand_environment_name(EnvironmentVariables.TOKEN_CACHE)
                ),
                **kwargs,
            )

        if self._credential:
            _logger.info("Environment is configured for %s", self._credential.__class__.__name__)
        else:
            expected_variables = set(
                EnvironmentVariables.TOKEN_VARS + EnvironmentVariables.MSAL_INTERACTIVE_VARS
            )
            set_variables = [v for v in expected_variables if v in os.environ]
            if set_variables:
                _logger.warning(
                    "Incomplete environment configuration. These variables are set: %s",
                    ", ".join(set_variables),
                )
            else:
                _logger.warning("No environment configuration found.")

    def _expand_environment_name(self, name: str):
        return name if self._prefix is None else f"{self._prefix}_{name}"

    def get_token(self, **kwargs) -> str:
        """Get token, deferring to the relevant credential class"""

        if not self._credential:
            message = "OsduEnvironmentCredential unavailable. Environment variables are not fully configured."
            raise CredentialUnavailableError(message=message)
        return self._credential.get_token(**kwargs)
