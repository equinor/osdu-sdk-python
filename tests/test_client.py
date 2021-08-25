# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for base OSDU client"""

from unittest.case import TestCase

from mock import patch
from osdu.client import OsduClient
from osdu.identity import OsduTokenCredential


class TestOsduClient(TestCase):
    """Test cases for base OSDU client"""

    def test_init(self):
        """Test the init method"""
        server_url = "http://www.test.com"
        credential = OsduTokenCredential(None, None, None, None)
        partition = 'opendes'
        retries = 2

        client = OsduClient(server_url, partition, credential, retries)

        self.assertEqual(server_url, client.server_url)
        self.assertEqual(partition, client.data_partition)
        self.assertEqual(credential, client.credentials)
        self.assertEqual(retries, client.retries)

    def test_init_defaults(self):
        """Test any init method default values are set accordingly"""

        client = OsduClient(None, None, None)

        self.assertEqual(0, client.retries)

    @patch.object(OsduTokenCredential, 'get_token', return_value=('ACCESS_TOKEN'))
    def test_get_headers(self, mock_get_token):  # pylint: disable=W0613
        """Test get_headers returns expected headers"""
        server_url = "http://www.test.com"
        partition = 'opendes'
        credential = OsduTokenCredential(None, None, None, None)
        expected = {
            'Content-Type': 'application/json',
            'data-partition-id': 'opendes',
            'Authorization': 'Bearer ACCESS_TOKEN'
        }
        client = OsduClient(server_url, partition, credential)
        headers = client.get_headers()

        self.assertDictEqual(expected, headers)


if __name__ == '__main__':
    import nose2
    nose2.main()
