# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for refresh token OSDU client"""

from unittest.case import TestCase

from osdu.identity import OsduMsalInteractiveCredential


class TestOsduMsalInteractiveIdentity(TestCase):
    """Test cases for refresh token OSDU client"""

    def test_init(self):
        """Test the init method"""
        client_id = 'client_id'
        authority = 'authority'
        scopes = 'scopes'
        token_cache = '.'

        # pylint: disable=too-many-function-args
        client = OsduMsalInteractiveCredential(client_id, authority, scopes, token_cache)

        res_client_id = client.client_id
        self.assertEqual(client_id, res_client_id)
        self.assertEqual(authority, client.authority)
        self.assertEqual(scopes, client.scopes)
        self.assertEqual(token_cache, client.token_cache)

    def test_init_defaults(self):
        """Test any init method default values are set accordingly"""

        client = OsduMsalInteractiveCredential(None, None, None)

        self.assertIsNone(client.token_cache)

    # TO DO: Get tokens and refresh needs test coverage
    # def test_get_token_no_refresh_needed(self):
    #     """Test getting the access token returns the stored version when no refresh is needed"""
    #     access_token ='my_access_token'
    #     tomorrow = datetime.now() + datetime.timedelta(days=1)
    #     client = OsduTokenClient(None, None, None, None, None, None)
    #     client.__access_token = access_token            # pylint: disable=protected-access
    #     client.__access_token_expire_date = tomorrow    # pylint: disable=protected-access
    #     returned_access_token = client.get_token()

    #     self.assertEqual(returned_access_token, access_token)


if __name__ == '__main__':
    import nose2
    nose2.main()
