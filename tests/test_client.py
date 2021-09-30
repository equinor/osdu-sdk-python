# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for base OSDU client"""

from unittest.case import TestCase

import mock
from mock import patch
from nose2.tools import params
from requests.models import HTTPError

from osdu.client import OsduClient
from osdu.identity import OsduTokenCredential


def create_dummy_client(server_url="http://www.test.com"):
    """Create a dummy client"""
    credential = OsduTokenCredential(None, None, None, None)
    partition = "opendes"
    retries = 2

    client = OsduClient(server_url, partition, credential, retries)
    return client


class TestOsduClient(TestCase):
    """Test cases for base OSDU client"""

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

    # region test get_returning_json
    @params((None, 200), ([200], 200), ([200, 202], 202), ([202], 202))
    def test_get_returning_json(self, expected_status_codes, actual_status_code):
        """Test valid get returns expected values"""
        expected_response_data = {
            "name": "value",
        }
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=actual_status_code)
        ok_response_mock.json.return_value = expected_response_data
        with mock.patch("osdu.client.OsduClient.get", return_value=ok_response_mock) as mock_get:
            client = create_dummy_client()

            if expected_status_codes:
                response = client.get_returning_json("http://www.test.com/", expected_status_codes)
            else:
                response = client.get_returning_json("http://www.test.com/")

            mock_get.assert_called_once()
            mock_get.assert_called_with("http://www.test.com/")
            self.assertDictEqual(expected_response_data, response)

    @params((None, 404), (None, 201), ([200], 404), ([200, 202], 500))
    def test_get_returning_json_http_error_throws_exception(
        self, expected_status_codes, actual_status_code
    ):
        """Test getting causing http error returns expected values"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=actual_status_code)
        with mock.patch("osdu.client.OsduClient.get", return_value=error_response_mock):
            with self.assertRaises(HTTPError):
                client = create_dummy_client()
                if expected_status_codes:
                    _ = client.get_returning_json("http://www.test.com/", expected_status_codes)
                else:
                    _ = client.get_returning_json("http://www.test.com/")

    # endregion test get_returning_json

    # region test post_returning_json
    @params((None, 200), ([200], 200), ([200, 202], 202), ([202], 202))
    def test_post_returning_json(self, expected_status_codes, actual_status_code):
        """Test valid post returns expected values"""
        input_data = {
            "name": "value",
        }
        expected_response_data = input_data
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=actual_status_code)
        ok_response_mock.json.return_value = expected_response_data
        with mock.patch("osdu.client.OsduClient.post", return_value=ok_response_mock) as mock_get:
            client = create_dummy_client()

            if expected_status_codes:
                response = client.post_returning_json(
                    "http://www.test.com/", input_data, expected_status_codes
                )
            else:
                response = client.post_returning_json("http://www.test.com/", input_data)

            mock_get.assert_called_once()
            mock_get.assert_called_with("http://www.test.com/", input_data)
            self.assertDictEqual(expected_response_data, response)

    @params((None, 404), (None, 201), ([200], 404), ([200, 202], 500))
    def test_post_returning_json_http_error_throws_exception(
        self, expected_status_codes, actual_status_code
    ):
        """Test post error returns expected values"""
        input_data = {
            "name": "value",
        }
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=actual_status_code)
        with mock.patch("osdu.client.OsduClient.post", return_value=error_response_mock):
            with self.assertRaises(HTTPError):
                client = create_dummy_client()
                if expected_status_codes:
                    _ = client.post_returning_json(
                        "http://www.test.com/", input_data, expected_status_codes
                    )
                else:
                    _ = client.post_returning_json("http://www.test.com/", input_data)

    # endregion test post_returning_json

    # region test delete
    @params((None, 200), ([200], 200), ([200, 202], 202), ([202], 202))
    @patch.object(OsduClient, "get_headers", return_value=(None))
    def test_delete(self, expected_status_codes, actual_status_code, _):
        """Test valid delete returns expected values"""
        expected_response_data = {
            "name": "value",
        }
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=actual_status_code)
        ok_response_mock.json.return_value = expected_response_data
        with mock.patch("requests.delete", return_value=ok_response_mock) as mock_delete:
            client = create_dummy_client()

            if expected_status_codes:
                response = client.delete("http://www.test.com/", expected_status_codes)
            else:
                response = client.delete("http://www.test.com/")

            mock_delete.assert_called_once()
            mock_delete.assert_called_with("http://www.test.com/", headers=None)
            self.assertEqual(ok_response_mock, response)

    @params((None, 404), (None, 201), ([200], 404), ([200, 202], 500))
    @patch.object(OsduClient, "get_headers", return_value=(None))
    def test_delete_http_error_throws_exception(self, expected_status_codes, actual_status_code, _):
        """Test delete http error returns expected values"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=actual_status_code)
        with mock.patch("requests.delete", return_value=error_response_mock):
            with self.assertRaises(HTTPError):
                client = create_dummy_client()
                if expected_status_codes:
                    _ = client.delete("http://www.test.com/", expected_status_codes)
                else:
                    _ = client.delete("http://www.test.com/")

    # endregion test delete


if __name__ == "__main__":
    import nose2

    nose2.main()
