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
from osdu.identity import OsduTokenCredential
from osdu.search import SearchClient
from osdu.search._client import VALID_SEARCH_API_VERSIONS


def create_dummy_client(server_url="http://www.test.com"):
    """Create a dummy client"""
    credential = OsduTokenCredential(None, None, None, None)
    partition = "opendes"
    retries = 2

    client = OsduClient(server_url, partition, credential, retries)
    return client


class TestSearchClient(TestCase):
    """Test cases for SearchClient"""

    # region test __init
    @params(
        (2, 2),
        ("latest", 2),
    )
    def test_init_valid_all_parameters(self, version, expected_version):
        """Test the init method with valid values for all parameters"""
        client = create_dummy_client()
        search_client = SearchClient(client, version)

        self.assertEqual(client, search_client._client)  # pylint: disable=protected-access
        self.assertEqual("search", search_client.service_name)
        self.assertListEqual(VALID_SEARCH_API_VERSIONS, search_client.valid_service_versions)
        self.assertEqual(expected_version, search_client.service_version)

    # endregion test __init

    # region test is_healthy
    def test_is_healthy(self):
        """Test the is_healthy end point"""
        ok_response_mock = mock.MagicMock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=200)
        with mock.patch("osdu.client.OsduClient.get", return_value=ok_response_mock):
            client = create_dummy_client()
            search_client = SearchClient(client)

            path = search_client.is_healthy()

            self.assertTrue(path)

    @params(404, 500)
    def test_is_healthy_error(self, status_code):
        """Test the is_healthy end point returning 404 error"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=status_code)
        with mock.patch("osdu.client.OsduClient.get", return_value=error_response_mock):
            client = create_dummy_client()
            search_client = SearchClient(client)

            path = search_client.is_healthy()

            self.assertFalse(path)

    # endregion test is_healthy

    # region test query_all_aggregated
    def test_query_all_aggregated(self):
        """Test the query_all_aggregated function"""
        request_data = {"kind": "*:*:*:*", "limit": 1, "query": "*", "aggregateBy": "kind"}
        expected_response_data = {
            "kind": "*:*:*:*",
            "limit": 1,
            "query": "*",
            "aggregateBy": "kind",
        }
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            search_client = SearchClient(client)

            response_data = search_client.query_all_aggregated()

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/search/v2/query", request_data
            )
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, "post_returning_json", side_effect=HTTPError(1))
    def test_query_all_aggregated_http_error(self, _):
        """Test query_all_aggregated http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            search_client = SearchClient(client)

            _ = search_client.query_all_aggregated()

    # endregion test query_all_aggregated

    # region test query_all_aggregated
    @params("id1", "id")
    def test_query_by_id(self, identifier):
        """Test the query_all_aggregated function"""
        request_data = {
            "kind": "*:*:*:*",
            "query": f'id:("{identifier}")',
        }
        expected_response_data = {"kind": "*:*:*:*", "limit": 1}
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            search_client = SearchClient(client)

            response_data = search_client.query_by_id(identifier)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/search/v2/query", request_data
            )
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, "post_returning_json", side_effect=HTTPError(1))
    def test_query_by_id_http_error(self, _):
        """Test query_all_aggregated http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            search_client = SearchClient(client)

            _ = search_client.query_by_id("id")

    # endregion test query_all_aggregated


if __name__ == "__main__":
    import nose2

    nose2.main()
