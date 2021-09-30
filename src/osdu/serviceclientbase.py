# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Base client for working with the OSDU file API."""

from typing import Union

from osdu.client import OsduClient


class ServiceClientBase:
    """Abstract base service client class for connecting with OSDU.
    It is not intended to use this directly, rather one of it's subclasses.
    """

    @property
    def service_name(self) -> str:
        """Get name of the service.
        By default used for constructing the url unless api_url is overwridden.

        Returns:
            str: Name of the service
        """
        return self._service_name

    @property
    def valid_service_versions(self) -> list:
        """List of valid service versions

        Returns:
            list: List of valid service versions
        """
        return self._valid_service_versions

    @property
    def service_version(self) -> int:
        """Version of the api being used

        Returns:
            int: Version of the api being used
        """
        return self._service_version

    def __init__(
        self,
        client: OsduClient,
        service_name: str,
        valid_service_versions: list,
        service_version: Union[int, str] = "latest",
    ):
        """Setup the ServiceClientBase

        Args:
            client (OsduClient): client to use for connection.
            service_name (str): service name.
            valid_service_versions (list): list of valid service versions
            service_version (Union[int, str], optional): service version (3 or 'latest') Defaults to 'latest'.

        Raises:
            ValueError: [description]
        """

        if not client or not isinstance(client, OsduClient):
            raise ValueError("client should be an OsduClient instance")

        if service_version not in valid_service_versions and service_version != "latest":
            raise ValueError(
                f"This package doesn't support API version '{service_version}'.\n"
                + f"Supported versions: {', '.join(str(v) for v in valid_service_versions)} or 'latest'"
            )

        self._client = client
        self._service_name = service_name
        self._valid_service_versions = valid_service_versions
        self._service_version = (
            self.valid_service_versions[-1] if service_version == "latest" else service_version
        )

    def api_url(self, extra_path: str = None):
        """Get a url for the api including any specified extra path

        Args:
            extra_path (str, optional): extra path to add to the base url. Defaults to None.

        Returns:
            str: api url
        """
        url = (
            self._client.server_url.rstrip("/")
            + f"/api/{self.service_name}/v{self.service_version}/"
        )
        if extra_path is not None:
            url = url + extra_path
        return url
