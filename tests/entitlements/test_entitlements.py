# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


"""Test cases for entitlements client"""

from unittest.case import TestCase

import mock
from nose2.tools import params
from requests.models import HTTPError

from osdu.client import OsduClient
from osdu.entitlements import EntitlementsClient
from osdu.entitlements._client import VALID_ENTITLEMENTS_API_VERSIONS
from osdu.identity import OsduTokenCredential


def create_dummy_client(server_url="http://www.test.com"):
    """Create a dummy client"""
    credential = OsduTokenCredential(None, None, None, None)
    partition = "opendes"
    retries = 2

    client = OsduClient(server_url, partition, credential, retries)
    return client


class TestEntitlementsClient(TestCase):
    """Test cases for EntitlementsClient"""

    # region test __init
    @params(
        (2, 2),
        ("latest", 2),
    )
    def test_init_valid_all_parameters(self, version, expected_version):
        """Test the init method with valid values for all parameters"""
        client = create_dummy_client()
        entitlements_client = EntitlementsClient(client, version)

        self.assertEqual(client, entitlements_client._client)  # pylint: disable=protected-access
        self.assertEqual("entitlements", entitlements_client.service_name)
        self.assertListEqual(
            VALID_ENTITLEMENTS_API_VERSIONS, entitlements_client.valid_service_versions
        )
        self.assertEqual(expected_version, entitlements_client.service_version)

    # endregion test __init

    # region test is_healthy
    def test_is_healthy(self):
        """Test valid call returns expected values"""
        ok_response_mock = mock.MagicMock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=200)
        with mock.patch("osdu.client.OsduClient.get", return_value=ok_response_mock):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            path = entitlements_client.is_healthy()

            self.assertTrue(path)

    @params(404, 500)
    def test_is_healthy_error(self, status_code):
        """Test valid call returns expected values"""
        error_response_mock = mock.MagicMock()
        type(error_response_mock).status_code = mock.PropertyMock(return_value=status_code)
        with mock.patch("osdu.client.OsduClient.get", return_value=error_response_mock):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            path = entitlements_client.is_healthy()

            self.assertFalse(path)

    # endregion test is_healthy

    # region test list_groups
    def test_list_groups(self):
        """Test valid call returns expected values"""
        expected_response_data = {
            "name": "service.schema-service.viewers",
            "description": "Datalake Schema admins",
            "email": "service.schema-service.admin@opendes.contoso.com",
        }
        with mock.patch(
            "osdu.client.OsduClient.get_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            response_data = entitlements_client.list_groups()

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/entitlements/v2/groups"
            )
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, "get", side_effect=HTTPError(1))
    def test_list_groups_http_error(self, _):
        """Test http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            _ = entitlements_client.list_groups()

    # endregion test list_groups

    # region test list_group_members
    @params("group1@asdf.com", "group2@asdf.com")
    def test_list_group_members(self, group):
        """Test valid call returns expected values"""
        expected_response_data = {
            "name": "service.schema-service.viewers",
            "description": "Datalake Schema admins",
            "email": "service.schema-service.admin@opendes.contoso.com",
        }
        with mock.patch(
            "osdu.client.OsduClient.get_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            response_data = entitlements_client.list_group_members(group)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                f"http://www.test.com/api/entitlements/v2/groups/{group}/members"
            )
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, "get", side_effect=HTTPError(1))
    def test_list_group_members_http_error(self, _):
        """Test http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            _ = entitlements_client.list_group_members("group1@asdf.com")

    # endregion test list_group_members

    # region test add_group
    @params("group1@asdf.com", "group2@asdf.com")
    def test_add_group_required_parameters(self, group):
        """Test valid call returns expected values"""
        request_data = {"name": group}
        expected_response_data = {
            "description": "",
            "name": group,
            "email": f"{group}@opendes.contoso.com",
        }
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            response_data = entitlements_client.add_group(group)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/entitlements/v2/groups", request_data, [200, 201]
            )
            self.assertEqual(expected_response_data, response_data)

    @params(
        ("group1@asdf.com", "desc"),
        ("group2@asdf.com", "desc 2"),
    )
    def test_add_group_description(self, group, description):
        """Test valid call returns expected values"""
        request_data = {"name": group, "description": description}
        expected_response_data = {
            "description": description,
            "name": group,
            "email": f"{group}@opendes.contoso.com",
        }
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            response_data = entitlements_client.add_group(group, description)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                "http://www.test.com/api/entitlements/v2/groups", request_data, [200, 201]
            )
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, "get", side_effect=HTTPError(1))
    def test_add_group_http_error(self, _):
        """Test http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            _ = entitlements_client.list_group_members("group1@asdf.com")

    # endregion test add_group

    # region test delete_group
    @params("group1@asdf.com", "group2@asdf.com")
    def test_delete_group(self, group):  # pylint: disable=no-self-use
        """Test valid call returns expected values"""
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=204)
        with mock.patch(
            "osdu.client.OsduClient.delete", return_value=ok_response_mock
        ) as mock_delete:
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            entitlements_client.delete_group(group)

            mock_delete.assert_called_once()
            mock_delete.assert_called_with(
                f"http://www.test.com/api/entitlements/v2/groups/{group}", [200, 204]
            )

    @mock.patch.object(OsduClient, "delete", side_effect=HTTPError(1))
    def test_delete_group_http_error(self, _):
        """Test http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            entitlements_client.delete_group("group1@asdf.com")

    # endregion test delete_group

    # region test add_member_to_group
    @params(
        ("member1@asdf.com", "group1@asdf.com", "MEMBER"),
        ("member2@asdf.com", "group2@asdf.com", "MEMBER"),
        ("member2@asdf.com", "group2@asdf.com", "OWNER"),
    )
    def test_add_member_to_group(self, member, group, role):
        """Test valid call returns expected values"""
        request_data = {"email": member, "role": role}
        expected_response_data = {"query": "*", "aggregateBy": "kind"}
        with mock.patch(
            "osdu.client.OsduClient.post_returning_json", return_value=expected_response_data
        ) as mock_post_returning_json:
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            response_data = entitlements_client.add_member_to_group(member, group, role)

            mock_post_returning_json.assert_called_once()
            mock_post_returning_json.assert_called_with(
                f"http://www.test.com/api/entitlements/v2/groups/{group}/members", request_data
            )
            self.assertEqual(expected_response_data, response_data)

    @mock.patch.object(OsduClient, "post_returning_json", side_effect=HTTPError(1))
    def test_add_member_to_group_http_error(self, _):
        """Test http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            _ = entitlements_client.add_member_to_group(
                "member1@asdf.com", "group1@asdf.com", "MEMBER"
            )

    # endregion test add_member_to_group

    # region test remove_member_from_group
    @params(
        ("member1@asdf.com", "group1@asdf.com"),
        ("member2@asdf.com", "group2@asdf.com"),
        ("member2@asdf.com", "group2@asdf.com"),
    )  # pylint: disable=no-self-use,R0201
    def test_remove_member_from_group(self, member, group):
        """Test valid call returns expected values"""
        ok_response_mock = mock.Mock()
        type(ok_response_mock).status_code = mock.PropertyMock(return_value=204)
        with mock.patch(
            "osdu.client.OsduClient.delete", return_value=ok_response_mock
        ) as mock_delete:
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)

            entitlements_client.remove_member_from_group(member, group)

            mock_delete.assert_called_once()
            mock_delete.assert_called_with(
                f"http://www.test.com/api/entitlements/v2/groups/{group}/members/{member}",
                [204],
            )

    @mock.patch.object(OsduClient, "delete", side_effect=HTTPError(1))
    def test_remove_member_from_group_http_error(self, _):
        """Test http errors are propogated"""
        with self.assertRaises(HTTPError):
            client = create_dummy_client()
            entitlements_client = EntitlementsClient(client)
            entitlements_client.remove_member_from_group("member1@asdf.com", "group1@asdf.com")

    # endregion test remove_member_from_group


if __name__ == "__main__":
    import nose2

    nose2.main()
