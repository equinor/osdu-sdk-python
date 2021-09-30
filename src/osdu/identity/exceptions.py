# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------


class CredentialUnavailableError(Exception):
    """The credential could not authenticate because required data or state is unavailable."""

    def __init__(self, message=None, **kwargs):
        self.message = str(message)
        super().__init__(kwargs)
