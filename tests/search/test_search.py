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

    # region test query
    @params(
        ("osdu:wks:dataset--File.Generic:1.0.0", None, None, None),
        ("*:*:*:*", None, None, None),
        (None, None, None, None),
        (None, "opendes:reference-data--ResourceSecurityClassification:RESTRICTED", None, None),
        (None, "opendes:reference-data--ResourceSecurityClassification:RESTRICTED", None, 20),
        (
            None,
            None,
            'data.WellboreID:("opendes:master-data--Wellbore:ad215042-05db-2b7e-e053-c818a488c79a")',
            None,
        ),
        (
            "*:*:*:*",
            "opendes:reference-data--ResourceSecurityClassification:RESTRICTED",
            None,
            None,
        ),
    )
    def test_query(self, kind, identifier, query, limit):
        """Test the query function"""
        request_data = {}

        if kind is None:
            request_data["kind"] = "*:*:*:*"
        else:
            request_data["kind"] = kind

        if identifier is not None:
            request_data["query"] = f'id:("{identifier}")'

        if query is not None:
            request_data["query"] = query

        if limit is not None:
            request_data["limit"] = limit

        # request_data = {
        #     "kind": request_kind,
        #     # "query": f'id:("{identifier}")',
        # }
        expected_response_data = {
            "results": [],
            "totalCount": 1,
        }
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            search_client = SearchClient(client)

            response_data = search_client.query(kind, identifier, query, limit)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/search/v2/query", request_data
            )
            self.assertEqual(expected_response_data, response_data)

    def test_query_cant_pass_id_and_query(self):
        """Test query with id and query faile"""
        with self.assertRaises(ValueError):
            client = create_dummy_client()
            search_client = SearchClient(client)

            _ = search_client.query(identifier="id", query="query")

    @mock.patch.object(OsduClient, "post_returning_json", side_effect=HTTPError(1))
    def test_query_http_error(self, _):
        """Test query http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            search_client = SearchClient(client)

            _ = search_client.query("kind")

    # endregion test query

    # region test query_by_id
    @params(
        ("id1", None),
        ("id1", 2),
        ("id", None),
        ("id", 2),
    )
    def test_query_by_id(self, identifier, limit):
        """Test the query_by_id function"""
        request_data = {
            "kind": "*:*:*:*",
            "query": f'id:("{identifier}")',
        }
        if limit is not None:
            request_data["limit"] = limit

        expected_response_data = {
            "results": [],
            "totalCount": 1,
        }
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            search_client = SearchClient(client)

            response_data = search_client.query_by_id(identifier, limit)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/search/v2/query", request_data
            )
            self.assertEqual(expected_response_data, response_data)

    @params("id1", "id")
    def test_query_by_id_defaults(self, identifier):
        """Test the query_by_id function"""
        request_data = {
            "kind": "*:*:*:*",
            "query": f'id:("{identifier}")',
        }

        expected_response_data = {
            "results": [],
            "totalCount": 1,
        }
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
        """Test query_by_id http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            search_client = SearchClient(client)

            _ = search_client.query_by_id("id")

    # endregion test query_by_id

    # region test query_by_kind
    @params(
        ("kind1", None),
        ("kind1", 2),
        ("kind", None),
        ("kind", 2),
    )
    def test_query_by_kind(self, kind, limit):
        """Test the query_by_kind function"""
        request_data = {
            "kind": kind,
        }
        if limit is not None:
            request_data["limit"] = limit

        expected_response_data = {
            "results": [],
            "totalCount": 1,
        }
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            search_client = SearchClient(client)

            response_data = search_client.query_by_kind(kind, limit)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/search/v2/query", request_data
            )
            self.assertEqual(expected_response_data, response_data)

    @params("kind1", "kind")
    def test_query_by_kind_defaults(self, kind):
        """Test the query_by_kind function"""
        request_data = {
            "kind": kind,
        }

        expected_response_data = {
            "results": [],
            "totalCount": 1,
        }
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            search_client = SearchClient(client)

            response_data = search_client.query_by_kind(kind)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/search/v2/query", request_data
            )
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, "post_returning_json", side_effect=HTTPError(1))
    def test_query_by_kind_http_error(self, _):
        """Test query_by_kind http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            search_client = SearchClient(client)

            _ = search_client.query_by_kind("kind")

    # endregion test query_by_kind


if __name__ == "__main__":
    import nose2

    nose2.main()
