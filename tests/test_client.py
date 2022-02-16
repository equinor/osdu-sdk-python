# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for base OSDU client"""

from unittest.case import TestCase

import mock
import requests
from mock import patch
from nose2.tools import params
from requests.models import HTTPError

from osdu.client import OsduClient
from osdu.identity import OsduTokenCredential

dummy_json = {
    "name": "value",
}


def create_dummy_client(server_url="http://www.test.com"):
    """Create a dummy client"""
    credential = OsduTokenCredential(None, None, None, None)
    partition = "opendes"
    retries = 2

    client = OsduClient(server_url, partition, credential, retries)
    return client


# pylint: disable=R0904
class TestOsduClient(TestCase):
    """Test cases for base OSDU client"""

    dummy_headers = {"headers": "value"}
    sample_json = {
        "name": "value",
    }

    def test_init(self):
        """Test the init method"""
        server_url = "http://www.test.com"
        credential = OsduTokenCredential(None, None, None, None)
        partition = "opendes"
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

    @patch.object(OsduTokenCredential, "get_token", return_value=("ACCESS_TOKEN"))
    def test_get_headers(self, mock_get_token):  # pylint: disable=W0613
        """Test get_headers returns expected headers"""
        expected_headers = {
            "Content-Type": "application/json",
            "data-partition-id": "opendes",
            "Authorization": "Bearer ACCESS_TOKEN",
        }
        client = create_dummy_client()
        headers = client.get_headers()

        self.assertDictEqual(expected_headers, headers)

    # region test get

    @params(
        ("http://www.test.com/", 200),
        ("http://www.test.com/test2/", 404),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_get(self, url, returned_status_code, _):
        """Test valid get returns expected values"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch.object(requests, "get", return_value=response_mock) as mock_get:
            client = create_dummy_client()

            response = client.get(url)

            mock_get.assert_called_once()
            mock_get.assert_called_with(url, headers=self.dummy_headers)
            self.assertEqual(response_mock, response)

    @params(
        ([200], 200),
        ([200, 202], 202),
        ([202], 202),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_get_status_codes_match_returns_ok(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test valid get returns ok when status-codes are provided"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.get", return_value=response_mock) as mock_delete:
            client = create_dummy_client()
            response = client.get("http://www.test.com/", expected_status_codes)

            mock_delete.assert_called_once()
            mock_delete.assert_called_with("http://www.test.com/", headers=self.dummy_headers)
            self.assertEqual(response_mock, response)

    @params(
        ([200], 404),
        ([200, 202], 500),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_get_status_codes_mismatch_throws_exception(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test get returns exception when status-codes are provided and return doeesn't match"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.get", return_value=error_response_mock) as _:
            with self.assertRaises(HTTPError):
                client = create_dummy_client()
                _ = client.get("http://www.test.com/", expected_status_codes)

    # endregion test get

    # region test get_returning_json

    @params(
        ("http://www.test.com/", 200),
        ("http://www.test.com/test2/", 404),
    )
    def test_valid_get_returning_json_required_params(self, url, returned_status_code):
        """Test valid get_returning_json returns expected values"""
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        ok_response_mock.json.return_value = dummy_json
        with mock.patch("osdu.client.OsduClient.get", return_value=ok_response_mock) as mock_get:
            client = create_dummy_client()

            response = client.get_returning_json(url)

            mock_get.assert_called_once()
            mock_get.assert_called_with(url, [200])
            self.assertDictEqual(dummy_json, response)

    @params(
        [200],
        [200, 202],
        [202],
    )
    def test_get_returning_json_status_codes(self, expected_status_codes):
        """Test valid get_returning_json returns ok when status-codes are provided"""
        ok_response_mock = mock.Mock()
        ok_response_mock.json.return_value = dummy_json
        with mock.patch("osdu.client.OsduClient.get", return_value=ok_response_mock) as mock_get:
            client = create_dummy_client()

            response = client.get_returning_json("http://www.test.com/", expected_status_codes)

            mock_get.assert_called_once()
            mock_get.assert_called_with("http://www.test.com/", expected_status_codes)
            self.assertDictEqual(dummy_json, response)

    # endregion test get_returning_json

    # region test post

    @params(
        ("string1", 200),
        ("string2", 404),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_valid_post_string_required_params(self, string_data, returned_status_code, _):
        """Test valid post with string returns expected values"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch.object(requests, "post", return_value=response_mock) as mock_post:
            client = create_dummy_client()

            response = client.post("http://www.test.com/", string_data)

            mock_post.assert_called_once()
            mock_post.assert_called_with(
                "http://www.test.com/", data=string_data, json=None, headers=self.dummy_headers
            )
            self.assertEqual(response_mock, response)

    @params(
        ({"name": "value"}, 200),
        ({"name2": "value2"}, 404),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_valid_post_json_required_params(self, json, returned_status_code, _):
        """Test valid post with json returns expected values"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch.object(requests, "post", return_value=response_mock) as mock_post:
            client = create_dummy_client()

            response = client.post("http://www.test.com/", json)

            mock_post.assert_called_once()
            mock_post.assert_called_with(
                "http://www.test.com/", data=None, json=json, headers=self.dummy_headers
            )
            self.assertEqual(response_mock, response)

    @params(
        ([200], 200),
        ([200, 202], 202),
        ([202], 202),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_post_status_codes_match_returns_ok(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test valid post returns ok when status-codes are provided"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.post", return_value=response_mock) as mock_delete:
            client = create_dummy_client()
            response = client.post("http://www.test.com/", "test data", expected_status_codes)

            mock_delete.assert_called_once()
            mock_delete.assert_called_with(
                "http://www.test.com/", data="test data", json=None, headers=self.dummy_headers
            )
            self.assertEqual(response_mock, response)

    @params(
        ([200], 404),
        ([200, 202], 500),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_post_status_codes_mismatch_throws_exception(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test post returns exception when status-codes are provided and return doeesn't match"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.post", return_value=error_response_mock) as _:
            with self.assertRaises(HTTPError):
                client = create_dummy_client()
                _ = client.post("http://www.test.com/", "test data", expected_status_codes)

    # endregion test post

    # region test post_returning_json

    @params(
        (dummy_json, 200),
        (dummy_json, 404),
        ("teststring", 202),
    )
    def test_valid_post_returning_json_required_params(self, data, returned_status_code):
        """Test valid post_returning_json returns expected values"""
        expected_response_data = dummy_json
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        ok_response_mock.json.return_value = expected_response_data
        with mock.patch("osdu.client.OsduClient.post", return_value=ok_response_mock) as mock_post:
            client = create_dummy_client()

            response = client.post_returning_json("http://www.test.com/", data)

            mock_post.assert_called_once()
            mock_post.assert_called_with("http://www.test.com/", data, [200])
            self.assertDictEqual(expected_response_data, response)

    @params(
        [200],
        [200, 202],
        [202],
    )
    def test_post_returning_json_status_codes(self, expected_status_codes):
        """Test valid post_returning_json returns ok when status-codes are provided"""
        ok_response_mock = mock.Mock()
        ok_response_mock.json.return_value = dummy_json
        with mock.patch("osdu.client.OsduClient.post", return_value=ok_response_mock) as mock_post:
            client = create_dummy_client()

            response = client.post_returning_json(
                "http://www.test.com/", dummy_json, expected_status_codes
            )

            mock_post.assert_called_once()
            mock_post.assert_called_with("http://www.test.com/", dummy_json, expected_status_codes)
            self.assertDictEqual(dummy_json, response)

    # endregion test post_returning_json

    # region test put

    @params(
        ("string1", 200),
        ("string2", 404),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_valid_put_string_required_params(self, string_data, returned_status_code, _):
        """Test valid put with string returns expected values"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch.object(requests, "put", return_value=response_mock) as mock_put:
            client = create_dummy_client()

            response = client.put("http://www.test.com/", string_data)

            mock_put.assert_called_once()
            mock_put.assert_called_with(
                "http://www.test.com/", data=string_data, json=None, headers=self.dummy_headers
            )
            self.assertEqual(response_mock, response)

    @params(
        ({"name": "value"}, 200),
        ({"name2": "value2"}, 404),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_valid_put_json_required_params(self, json, returned_status_code, _):
        """Test valid put with json returns expected values"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch.object(requests, "put", return_value=response_mock) as mock_put:
            client = create_dummy_client()

            response = client.put("http://www.test.com/", json)

            mock_put.assert_called_once()
            mock_put.assert_called_with(
                "http://www.test.com/", data=None, json=json, headers=self.dummy_headers
            )
            self.assertEqual(response_mock, response)

    @params(
        ([200], 200),
        ([200, 202], 202),
        ([202], 202),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_put_status_codes_match_returns_ok(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test valid put returns ok when status-codes are provided"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.put", return_value=response_mock) as mock_delete:
            client = create_dummy_client()
            response = client.put("http://www.test.com/", "test data", expected_status_codes)

            mock_delete.assert_called_once()
            mock_delete.assert_called_with(
                "http://www.test.com/", data="test data", json=None, headers=self.dummy_headers
            )
            self.assertEqual(response_mock, response)

    @params(
        ([200], 404),
        ([200, 202], 500),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_put_status_codes_mismatch_throws_exception(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test put returns exception when status-codes are provided and return doeesn't match"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.put", return_value=error_response_mock) as _:
            with self.assertRaises(HTTPError):
                client = create_dummy_client()
                _ = client.put("http://www.test.com/", "test data", expected_status_codes)

    # endregion test put

    # region test put_returning_json

    @params(
        (dummy_json, 200),
        (dummy_json, 404),
        ("teststring", 202),
    )
    def test_valid_put_returning_json_required_params(self, data, returned_status_code):
        """Test valid put returns expected values"""
        expected_response_data = dummy_json
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        ok_response_mock.json.return_value = expected_response_data
        with mock.patch("osdu.client.OsduClient.put", return_value=ok_response_mock) as mock_put:
            client = create_dummy_client()

            response = client.put_returning_json("http://www.test.com/", data)

            mock_put.assert_called_once()
            mock_put.assert_called_with("http://www.test.com/", data, [200])
            self.assertDictEqual(expected_response_data, response)

    @params(
        [200],
        [200, 202],
        [202],
    )
    def test_put_returning_json_status_codes(self, expected_status_codes):
        """Test valid put_returning_json returns ok when status-codes are provided"""
        ok_response_mock = mock.Mock()
        ok_response_mock.json.return_value = dummy_json
        with mock.patch("osdu.client.OsduClient.put", return_value=ok_response_mock) as mock_put:
            client = create_dummy_client()

            response = client.put_returning_json(
                "http://www.test.com/", dummy_json, expected_status_codes
            )

            mock_put.assert_called_once()
            mock_put.assert_called_with("http://www.test.com/", dummy_json, expected_status_codes)
            self.assertDictEqual(dummy_json, response)

    # endregion test put_returning_json

    # region test delete
    @params(
        ("http://www.test.com/", 200),
        ("http://www.test.com/", 404),
        ("http://www.test.com/test2/", 201),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_valid_delete_required_params(self, url, returned_status_code, _):
        """Test valid delete returns expected values"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.delete", return_value=response_mock) as mock_delete:
            client = create_dummy_client()
            response = client.delete(url)

            mock_delete.assert_called_once()
            mock_delete.assert_called_with(url, headers=self.dummy_headers)
            self.assertEqual(response_mock, response)

    @params(
        ([200], 200),
        ([200, 202], 202),
        ([202], 202),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_delete_status_codes_match_returns_ok(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test valid delete returns ok when status-codes are provided"""
        response_mock = mock.Mock()
        type(response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.delete", return_value=response_mock) as mock_delete:
            client = create_dummy_client()
            response = client.delete("http://www.test.com/", expected_status_codes)

            mock_delete.assert_called_once()
            mock_delete.assert_called_with("http://www.test.com/", headers=self.dummy_headers)
            self.assertEqual(response_mock, response)

    @params(
        ([200], 404),
        ([200, 202], 500),
    )
    @patch.object(OsduClient, "get_headers", return_value=dummy_headers)
    def test_delete_status_codes_mismatch_throws_exception(
        self, expected_status_codes, returned_status_code, _
    ):
        """Test delete returns exception when status-codes are provided and return doeesn't match"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=returned_status_code)
        with mock.patch("requests.delete", return_value=error_response_mock) as _:
            with self.assertRaises(HTTPError):
                client = create_dummy_client()
                _ = client.delete("http://www.test.com/", expected_status_codes)

    # endregion test delete


if __name__ == "__main__":
    import nose2

    nose2.main()
