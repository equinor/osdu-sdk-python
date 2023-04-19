# OSDU SDK for Python

[![Build](https://github.com/equinor/osdu-sdk-python/actions/workflows/build.yml/badge.svg)](https://github.com/equinor/osdu-cli/actions/workflows/build.yml)
[![License](https://img.shields.io/pypi/l/osdu-sdk.svg)](https://github.com/equinor/osdu-sdk-python/blob/master/LICENSE.md)
[![PyPi Version](https://img.shields.io/pypi/v/osdu-sdk.svg?color=informational)](https://pypi.org/project/osdu/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/osdu-sdk.svg?color=informational)](https://pypi.org/project/osdu-sdk/)
![Unknown coverage](https://img.shields.io/badge/coverage-%3F%3F%3F-important)

This is the OSDU SDK for Python (work in progress).

:warning: Note that this is a work in progress and is not complete / might contain bugs and might be subject to breaking changes.

Please give your feedback by [raising an issue](#contributing).

## Installation

Usage requires that you have a valid python 3.8+ installation on your machine. You might also consider creating a seperate python [virtual environment](https://docs.python.org/3/library/venv.html) for working with OSDU.

For general usage deploying from [PyPi](https://pypi.org/project/osdu-sdk/) is the easiest and recommended method.

```bash
pip install osdu-sdk
```

If you want to modify the sdk code then see the [development wiki](https://github.com/equinor/osdu-sdk-python/wiki) for alternative setup steps.

## Usage


1. Import necessary items

```
from osdu.client import OsduClient
from osdu.identity import OsduTokenCredential, OsduMsalInteractiveCredential, OsduEnvironmentCredential
```

2. Create an instance of OsduTokenCredential, OsduMsalInteractiveCredential, OsduEnvironmentCredential or your own custom class.

```
credential = OsduMsalInteractiveCredential(client_id, authority, scopes, token_cache)

```
On-behalf-of flow using a middle-tier service principal

```python
from osdu.identity import OsduMsalOnBehalfOf, OsduMsalDeviceCode
interactive_client = OsduMsalDeviceCode(<CLIENT_ID>,"https://login.microsoftonline.com/{TENANT_ID}","{CLIENT_ID}/.default","./cache")
obo_client = OsduMsalOnBehalfOf(interactive_client,<CLIENT_SECRET>,<OSDU_RESOURCE_ID>)
obo_client.get_token()

```


3. Create a client

```
client = OsduClient(server, partition, credential)
```

4. Use the REST interface to call OSDU API's

```
response = client.get(client.server_url + '/api/search/v2/health/readiness_check')
print(f"Search service: {response.status_code}\t {response.reason}")
```

For a full example see [examples/example.py](https://github.com/equinor/osdu-sdk-python/blob/master/examples/example.py)

## Contributing

We welcome any kind of contribution, whether it be reporting issues or sending pull requests.

When contributing to this repository abide by the
[Equinor Open Source Code of Conduct](https://github.com/equinor/opensource/blob/master/CODE_OF_CONDUCT.md).


### CLI specific issues and requests

If your issue is relevant to the OSDU CLI, please use this repositories [issue tracker](https://github.com/equinor/osdu-sdk-python/issues).

Be sure to search for similar previously reported issues prior to creating a new one.
In addition, here are some good practices to follow when reporting issues:

- Add a `+1` reaction to existing issues that are affecting you
- Include verbose output (`--debug` flag) when reporting unexpected error messages
- Include the version of OSDU SDK for Python installed, `pip show osdu` will report this
- Include the version of OSDU you are using

### Code changes

See the
[wiki page on contributing](https://github.com/equinor/osdu-sdk-python/wiki) for
more information on submitting code changes.
