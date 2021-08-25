# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""Base credential for authentication with OSDU."""

from abc import ABC, abstractmethod


# pylint: disable=too-few-public-methods
class OsduBaseCredential(ABC):
    """Abstract base credential class for connecting with OSDU.
    It is not intended to use this directly, rather one of it's subclasses.
    """

    @abstractmethod
    def get_token(self, **kwargs) -> str:
        """Get access token, trying to refresh if needed."""
