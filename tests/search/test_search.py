# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for search client"""

from unittest.case import TestCase

import mock
from nose2.tools import params
from requests.models import HTTPError

from osdu.client import OsduClient
from osdu.identity._credential.token import OsduTokenCredential
from osdu.search import SearchClient


def create_dummy_client(server_url="http://www.test.com"):
    """Create a dummy client"""
    credential = OsduTokenCredential(None, None, None, None)
    partition = 'opendes'
    retries = 2

    client = OsduClient(server_url, partition, credential, retries)
    return client


class TestSearchClient(TestCase):
    """Test cases for SearchClient"""

    # region test __init
    @params(
        (2, 2),
        ('latest', 2),
    )
    def test_init(self, version, expected_version):
        """Test the init method for token credentials"""
        client = create_dummy_client()
        search_client = SearchClient(client, version)

        self.assertEqual(client, search_client._client)  # pylint: disable=protected-access
        self.assertEqual(expected_version, search_client.version)

    def test_init_invalid_client(self):
        """Test the init method for token credentials"""

        with self.assertRaises(ValueError):
            _ = SearchClient(None)

        with self.assertRaises(ValueError):
            _ = SearchClient("This is not an OsduClient")

    def test_init_invalid_version(self):
        """Test the init method for token credentials"""
        client = create_dummy_client()

        with self.assertRaises(ValueError):
            _ = SearchClient(client, 0)

        with self.assertRaises(ValueError):
            _ = SearchClient(client, 9999)

        with self.assertRaises(ValueError):
            _ = SearchClient(client, "This is not a valid version")
    # endregion test __init

    # region test api_url
    @params(
        ("http://www.test.com", "extra_path", 2),
        ("http://www.test.com", "extra_path2", 2),
        ("http://www.test2.com", "extra_path", 2),
        ("http://www.test2.com/", "extra_path", 2),
        ("http://www.test2.com/", "extra_path", 'latest'),
    )
    def test_api_url(self, server_url, extra_path, version):
        """Test getting the api path returns expected values"""
        client = create_dummy_client(server_url)
        search_client = SearchClient(client, version)

        path = search_client.api_url(extra_path)

        if version == "latest":
            version = 2
        self.assertEqual(f"{server_url.rstrip('/')}/api/search/v{version}/{extra_path}", path)

    def test_api_url_no_extra_path(self):
        """Test getting the api path returns expected values"""
        client = create_dummy_client()
        search_client = SearchClient(client)

        path = search_client.api_url()

        self.assertEqual("http://www.test.com/api/search/v2/", path)
    # endregion test api_url

    # region test is_healthy
    def test_is_healthy(self):
        """Test getting the api path returns expected values"""
        ok_response_mock = mock.MagicMock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=200)
        with mock.patch('osdu.client.OsduClient.get', return_value=ok_response_mock):
            client = create_dummy_client()
            search_client = SearchClient(client)

            path = search_client.is_healthy()

            self.assertTrue(path)

    @params(404, 500)
    def test_is_healthy_error(self, status_code):
        """Test getting the api path returns expected values"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=status_code)
        with mock.patch('osdu.client.OsduClient.get', return_value=error_response_mock):
            client = create_dummy_client()
            search_client = SearchClient(client)

            path = search_client.is_healthy()

            self.assertFalse(path)
    # endregion test is_healthy

    # region test query_all_aggregated
    def test_query_all_aggregated(self):
        """Test getting the api path returns expected values"""
        request_data = {
            "kind": "*:*:*:*",
            "limit": 1,
            "query": "*",
            "aggregateBy": "kind"
        }
        expected_response_data = {
            "kind": "*:*:*:*",
            "limit": 1,
            "query": "*",
            "aggregateBy": "kind"
        }
        ok_response_mock = mock.MagicMock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=200)
        with mock.patch('osdu.client.OsduClient.post_returning_json',
                        return_value=expected_response_data) as mock_post_returning_json:
            client = create_dummy_client()
            search_client = SearchClient(client)

            response_data = search_client.query_all_aggregated()

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with('http://www.test.com/api/search/v2/query', request_data)
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, 'post_returning_json', side_effect=HTTPError(1))
    def test_query_all_aggregated_http_error(self, _):
        """Test http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            search_client = SearchClient(client)

            _ = search_client.query_all_aggregated()
    # endregion test query_all_aggregated


if __name__ == '__main__':
    import nose2
    nose2.main()
