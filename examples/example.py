# -----------------------------------------------------------------------------
# Copyright (c) Equinor ASA. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""Example code for calling the osdu search endpoint"""

import json
from os.path import expanduser

from osdu.client import OsduClient
from osdu.identity import OsduMsalInteractiveCredential
from osdu.search import SearchClient


def main():
    """Example code for calling the osdu search endpoint"""

    # Values needed for msal interactive credentials.
    # See also OsduTokenCredential and OsduEnvironmentCredential for alternatives.
    client_id = "7a414874-4b27-4378-b34f-bc9e5a5faa4f"
    resource_id = "ea31113d-90a2-47bf-befe-26c134b6354d"

    authority = "https://login.microsoftonline.com/3aa4a235-b6e2-48d5-9195-7fcf05b459b0"
    scopes = f"{resource_id}/.default openid"
    token_cache = expanduser("~/.osdu-example-token-cache")
    credential = OsduMsalInteractiveCredential(client_id, authority, scopes, token_cache)

    # Create the client
    client = OsduClient("https://020.api.osdu.equinor.com", "opendes", credential)

    # Direct REST: Check the service status then post json data
    response = client.get(client.server_url + "/api/search/v2/health/readiness_check")
    print(f"Search service: {response.status_code}\t {response.reason}")

    request_data = {
        "kind": "*:*:*:*",
        "limit": 1,
        "query": "*",
        "aggregateBy": "kind",
    }
    response_json = client.post_returning_json(
        client.server_url + "/api/search/v2/query", request_data
    )
    print(json.dumps(response_json, indent=2))

    # Search client: Status then query aggregated
    search_client = SearchClient(client)

    print(f"Search is Up: {search_client.is_healthy()}")

    response_json = search_client.query_all_aggregated()
    print(json.dumps(response_json, indent=2))


if __name__ == "__main__":
    main()
