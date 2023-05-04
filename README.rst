# OSDU SDK for Python
=====================

This is the OSDU SDK for Python (work in progress).

Usage
=====

Note: This is currently a WIP so will be subject to breaking changes.

Change Log
==========

0.0.14
------

- Fix for msal non-interactive authentication

0.0.13
------

- Add support for non-interactive authentication

0.0.12
------

- Add entitlements group description parameter
  
0.0.11
------

- All client action functions can optional expected response status codes
                   
0.0.10
------

- Delete doesn't check status codes (consistency with other functions)
- Put will pass list objects as json
                   
0.0.9
-----

- Search query_by_kind function
- Search query_by_id supports limit
- Search query supports a specific query
                   
0.0.8
-----

- search query supports limit

0.0.7
-----

- client put & put_returning_json functions
  
0.0.6
-----

- entitlements add_member_to_group role parameter
- added entitlements remove_member_from_group function
 
0.0.5
-----

- Search query function
      
0.0.4
-----

- Search query_by_id function

0.0.3
-----

- Reusable client base
- Entitlements client

0.0.2
-----

- Add basic search client
  
0.0.1
-----

- Initial release.
