from requests import post, get
from tdw.webgl.dashboard.request import Request
from tdw.webgl.dashboard.session import Session, from_json


"""
Test the Dashboard.

To run:

In one shell:

1. cd tdw/Python/tdw/webgl/dashboard
2. python3 dashboard.py

In another shell:

1. cd tdw/Python/webgl/tests
2. python3 dashboard_client.py

If the test succeeds, it doesn't print any messages or errors.
Close the first shell when the test is done.
"""

base_url = 'http://127.0.0.1:1453/api'
# Create a session.
resp = post(f'{base_url}/create')
assert resp.status_code == 200, resp.status_code
assert resp.text == '0', resp.text
session_id = int(resp.text)
assert session_id == 0, session_id
url = f'{base_url}/{session_id}'
# Get the session.
resp = get(url)
assert resp.status_code == 200, resp.status_code
assert resp.text == '{"id": 0, "request": "none", "response": "none", "message": ""}', resp.text
session = from_json(resp.text)
assert session.session_id == 0, session.session_id
assert session.request == Request.none, session.request
assert session.message == "", session.response
# Set the session.
session = Session(session_id=0, request=Request.get_start_time)
resp = post(url, data=session.to_json())
assert resp.status_code == 200, resp.status_code
session = from_json(get(url).text)
assert session.request == Request.get_start_time, session.request
# Set the request.
session = Session(session_id=0, request=Request.none)
post(url, data=session.to_json())
resp = post(f'{url}/{Request.get_trial_name.name}')
assert resp.status_code == 200, resp.status_code
session = from_json(get(url).text)
assert session.request == Request.get_trial_name, session.request
# Invalid URLs.
resp = post(url)
assert resp.status_code != 200, resp.status_code
resp = get(f'{base_url}/1')
assert resp.status_code == 200, resp.status_code
assert resp.text != '1', resp.text
resp = get(f'{url}/{Request.get_trial_name.name}')
assert resp.status_code != 200, resp.status_code
resp = post(f'{url}/fake_request')
assert resp.status_code == 200, resp.status_code
assert resp.text != 'ok', resp.text
