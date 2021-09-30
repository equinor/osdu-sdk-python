# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Constants for identity"""


# pylint: disable=too-few-public-methods
class EnvironmentVariables:
    """Environment variable names"""

    CLIENT_ID = "CLIENT_ID"
    CLIENT_SECRET = "CLIENT_SECRET"
    TOKEN_ENDPOINT = "TOKEN_ENDPOINT"
    REFRESH_TOKEN = "REFRESH_TOKEN"
    AUTHORITY = "AUTHORITY"
    SCOPES = "SCOPES"
    TOKEN_CACHE = "TOKEN_CACHE"

    TOKEN_VARS = (CLIENT_ID, CLIENT_SECRET, TOKEN_ENDPOINT, REFRESH_TOKEN)
    MSAL_INTERACTIVE_VARS = (CLIENT_ID, AUTHORITY, SCOPES)
