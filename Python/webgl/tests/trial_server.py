from time import sleep
from webbrowser import open_new_tab
from requests import get
import numpy as np
from tdw.output_data import FastTransforms
from tdw.webgl.utils import get_output_data, string_to_datetime


"""
TrialServer unit tests.

Usage:

1. Run the trial server with default argument values.
2. Run `webgl_test_server.py` with default argument values.
3. Run this script.

Result: 

- A new browser tab opens with the WebGL Build. It runs until it says that a researcher ended the session.
- No console output in the shell running this script
"""


def get_test(url: str):
    response = get(url)
    assert response.status_code == 200, response.status_code
    return response.text


def datetime_query(query: str):
    string_to_datetime(get_test(f'{query_url}{query}'))


base_url: str = 'http://127.0.0.1:1204/api/'
# Create a session.
launch_url = get_test(f'{base_url}create')
assert launch_url.startswith(f'{base_url}launch/')
# Get the session ID from the URL.
session_id: str = launch_url.split('/')[-1]
open_new_tab(launch_url)
query_url = f'http://127.0.0.1:1204/api/query/{session_id}/'
got_status = False
for i in range(100):
    r = get(f'{query_url}status')
    if r.status_code == 200:
        got_status = True
        assert r.text == 'running', r.text
        break
    else:
        sleep(5)
assert got_status
# Get the trial name.
text = get_test(f'{query_url}trialName')
assert text == 'TrialServerTest', text
# Test whether these are datetime strings.
datetime_query('startTime')
datetime_query('trialStartTime')
# The trial hasn't ended yet.
text = get_test(f'{query_url}trialEndTime')
assert text == '', text
# Get the output data.
text = get_test(f'{query_url}outputData')
# Parse the output data.
resp = get_output_data(text)
assert resp[0][4:8] == b'ftra', resp[0]
fast_transforms = FastTransforms(resp[0])
assert fast_transforms.get_num() == 1, fast_transforms.get_num()
# Test if the position is roughly (0, 0, 0)
position = fast_transforms.get_position(0)
mag = float(np.linalg.norm(position))
assert mag <= 1e-5, mag
# Kill the session.
get_test(f'http://127.0.0.1:1204/api/kill/{session_id}/')
