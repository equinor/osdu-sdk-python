# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Entitlements client for working with the OSDU entitlements API."""

from typing import Union

from osdu.client import OsduClient
from osdu.serviceclientbase import ServiceClientBase

VALID_ENTITLEMENTS_API_VERSIONS = [2]


class EntitlementsClient(ServiceClientBase):
    """A client for working with the OSDU Entitlements API."""

    def __init__(self, client: OsduClient, service_version: Union[int, str] = "latest"):
        """Setup the EntitlementsClient

        Args:
            client (OsduClient): client to use for connection
            service_version (Union[int, str], optional): service version (3 or 'latest') Defaults to 'latest'.

        Raises:
            ValueError: [description]
        """
        super().__init__(client, "entitlements", VALID_ENTITLEMENTS_API_VERSIONS, service_version)

    # def query():
    #     pass

    # def query_by_id():
    #     pass

    def is_healthy(self) -> bool:
        """Returns health status of the API

        Returns:
            bool: health status of the API
        """
        response = self._client.get(self.api_url("health/readiness_check"))
        return response.status_code == 200

    def list_groups(self) -> dict:
        """List groups

        Returns:
            dict: containing the result
        """
        response_json = self._client.get_returning_json(self.api_url("groups"))
        return response_json

    def list_group_members(self, group: str) -> dict:
        """List members in a group

        Args:
            group (str): The email of the group.

        Returns:
            dict: containing the result
        """
        response_json = self._client.get_returning_json(self.api_url(f"groups/{group}/members"))
        return response_json

    def add_group(self, group: str) -> dict:
        """Add a new group

        Args:
            group (str): The email of the group.

        Returns:
            dict: containing the result
        """
        request_data = {"name": group}
        response_json = self._client.post_returning_json(
            self.api_url("groups"), request_data, [200, 201]
        )
        return response_json

    def delete_group(self, group: str):
        """Delete a group

        Args:
            group (str): The email of the group.
        """
        _ = self._client.delete(self.api_url(f"groups/{group}"), [200, 204])

    def add_member_to_group(self, member: str, group: str, role: str) -> dict:
        """Add member to group

        Args:
            member (str): The email of the member to be added.
            group (str): The email of the group.
            role (str): The role in the group.

        Returns:
            dict: containing the result
        """
        request_data = {
            "email": member,
            "role": role,
        }
        response_json = self._client.post_returning_json(
            self.api_url(f"groups/{group}/members"), request_data
        )
        return response_json

    def remove_member_from_group(self, member: str, group: str):
        """Remove member from group

        Args:
            member (str): The email of the member to remove.
            group (str): The email of the group.
        """
        _ = self._client.delete(self.api_url(f"groups/{group}/members/{member}"), [204])
