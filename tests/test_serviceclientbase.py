# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for ServiceClientBase"""

from unittest.case import TestCase

from nose2.tools import params

from osdu.client import OsduClient
from osdu.identity._credential.token import OsduTokenCredential
from osdu.serviceclientbase import ServiceClientBase


def create_dummy_client(server_url="http://www.test.com"):
    """Create a dummy client"""
    credential = OsduTokenCredential(None, None, None, None)
    partition = "opendes"
    retries = 2

    client = OsduClient(server_url, partition, credential, retries)
    return client


class TestServiceClientBase(TestCase):
    """Test cases for SearchClient"""

    # region test __init
    @params(
        ([3], 3, 3),
        ([3, 4], 4, 4),
        ([2], "latest", 2),
    )
    def test_init_valid_all_parameters(self, valid_versions, version, expected_version):
        """Test the init method with valid values for all parameters"""
        client = create_dummy_client()
        service_client = ServiceClientBase(client, "service_name", valid_versions, version)

        self.assertEqual(client, service_client._client)  # pylint: disable=protected-access
        self.assertEqual(valid_versions, service_client.valid_service_versions)
        self.assertEqual(expected_version, service_client.service_version)

    def test_init_invalid_client(self):
        """Test the init method with invalid client"""

        with self.assertRaises(ValueError):
            _ = ServiceClientBase(None, "service_name", [2])

        with self.assertRaises(ValueError):
            _ = ServiceClientBase("This is not an OsduClient", "service_name", [2])

    def test_init_invalid_version(self):
        """Test the init method with invalid version"""
        client = create_dummy_client()

        with self.assertRaises(ValueError):
            _ = ServiceClientBase(client, "service_name", [], 0)

        with self.assertRaises(ValueError):
            _ = ServiceClientBase(client, "service_name", [1, 2], 9999)

    # endregion test __init

    # region test api_url
    @params(
        ("http://www.test.com", "service_name", "extra_path", [2], 2),
        ("http://www.another_test.com", "service_name", "extra_path", [2], 2),
        ("http://www.another_test.com/", "service_name", "extra_path", [2], 2),
        ("http://www.test.com", "another_service_name", "extra_path", [2], 2),
        ("http://www.test.com", "another_service_name", "extra_path", [2, 3], 3),
        ("http://www.test.com", "service_name", "extra_path2", [2], 2),
        ("http://www.test.com/", "service_name", "extra_path", [2], "latest"),
    )
    def test_api_url(self, server_url, service_name, extra_path, valid_versions, version):
        """Test getting the api path returns expected values"""
        client = create_dummy_client(server_url)
        search_client = ServiceClientBase(client, service_name, valid_versions, version)

        path = search_client.api_url(extra_path)
        self.assertEqual(
            f"{server_url.rstrip('/')}/api/{search_client.service_name}/v{search_client.service_version}/{extra_path}",
            path,
        )

    def test_api_url_no_extra_path(self):
        """Test getting the api path with no extra path returns expected values"""
        client = create_dummy_client()
        search_client = ServiceClientBase(client, "service_name", [2], 2)

        path = search_client.api_url()

        self.assertEqual("http://www.test.com/api/service_name/v2/", path)

    # endregion test api_url


if __name__ == "__main__":
    import nose2

    nose2.main()
