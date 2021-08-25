# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for refresh token OSDU client"""

import logging
import os
from unittest.case import TestCase
import mock

from testfixtures import LogCapture
from osdu.identity import OsduEnvironmentCredential
from osdu.identity.consts import EnvironmentVariables
from osdu.identity.exceptions import CredentialUnavailableError


class TestOsduEnvironmentCredential(TestCase):
    """Test cases for refresh token OSDU client"""

    def test_init_token(self):
        """Test the init method for token credentials"""
        envs = {
            EnvironmentVariables.CLIENT_ID: "CLIENT_ID",
            EnvironmentVariables.CLIENT_SECRET: "CLIENT_SECRET",
            EnvironmentVariables.TOKEN_ENDPOINT: "TOKEN_ENDPOINT",
            EnvironmentVariables.REFRESH_TOKEN: "REFRESH_TOKEN",
        }

        with mock.patch.dict(os.environ, envs, clear=True):
            with LogCapture(level=logging.INFO) as log_capture:
                client = OsduEnvironmentCredential()
                # pylint: disable=protected-access
                self.assertEqual('OsduTokenCredential', client._credential.__class__.__name__)
                self.assertEqual(len(log_capture.records), 1)

    def test_init_msal(self):
        """Test the init method for msal"""
        envs = {
            EnvironmentVariables.CLIENT_ID: "CLIENT_ID",
            EnvironmentVariables.AUTHORITY: "AUTHORITY",
            EnvironmentVariables.SCOPES: "SCOPES"
        }

        with mock.patch.dict(os.environ, envs, clear=True):
            with LogCapture(level=logging.INFO) as log_capture:
                client = OsduEnvironmentCredential()
                # pylint: disable=protected-access
                self.assertEqual('OsduMsalInteractiveCredential', client._credential.__class__.__name__)
                self.assertEqual(len(log_capture.records), 1)

    def test_init_msal_optional(self):
        """Test the init method for msal with optional arguments set"""
        envs = {
            EnvironmentVariables.CLIENT_ID: "CLIENT_ID",
            EnvironmentVariables.AUTHORITY: "AUTHORITY",
            EnvironmentVariables.SCOPES: "SCOPES",
            EnvironmentVariables.TOKEN_CACHE: "TOKEN_CACHE",
        }

        with mock.patch.dict(os.environ, envs, clear=True):
            client = OsduEnvironmentCredential()
            # pylint: disable=protected-access
            self.assertEqual('OsduMsalInteractiveCredential', client._credential.__class__.__name__)
            self.assertEqual('TOKEN_CACHE', client._credential.token_cache)

    def test_init_invalid(self):
        """Test incomplete setup doesn't assign any credentials."""
        envs = {}

        with mock.patch.dict(os.environ, envs, clear=True):
            with LogCapture(level=logging.WARN) as log_capture:
                client = OsduEnvironmentCredential()
                # pylint: disable=protected-access
                self.assertIsNone(client._credential)
                self.assertEqual(len(log_capture.records), 1)

    def test_get_token_invalid_fails(self):
        """Test incomplete setup throws exception for get_token())."""
        envs = {}

        with mock.patch.dict(os.environ, envs, clear=True):
            client = OsduEnvironmentCredential()
            with self.assertRaises(CredentialUnavailableError):
                client.get_token()


if __name__ == '__main__':
    import nose2
    nose2.main()
