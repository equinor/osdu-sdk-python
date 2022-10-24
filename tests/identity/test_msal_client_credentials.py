# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for get token OSDU client"""
import json

import mock

from unittest.case import TestCase
from osdu.identity import OsduMsalNonInteractiveCredential


class TestOsduMsalNonInteractiveCredential(TestCase):
    """Test cases for refresh token OSDU client"""

    _FAKE_TOKEN = json.loads('{"access_token": "token", "token_type": "Bearer", "expires_in": 100 }')

    def setUp(self):
        client_id = "client_id"
        client_secret = "client_secret"
        authority = "https://test.com/client_id"
        scopes = "scopes"
        self.auth = OsduMsalNonInteractiveCredential(client_id, client_secret, authority, scopes, None)
        self.auth._get_token = mock.MagicMock(return_value=self._FAKE_TOKEN)

    def test_get_token(self):
        self.assertEqual('token', self.auth.get_token())


if __name__ == "__main__":
    import nose2

    nose2.main()
