from os import getcwd
from typing import List
from time import sleep
from argparse import ArgumentParser
from subprocess import Popen
from webbrowser import open_new_tab
from requests import post, get
from sys import executable


def get_python_call(filename: str) -> List[str]:
    return [executable, filename]


parser = ArgumentParser(allow_abbrev=False)
parser.add_argument('--build', type=str, default='D:/tdw_webgl_test_builds/webgl',
                    help='The path to the folder containing the local WebGL Build')
args, unknown = parser.parse_known_args()
base_url = 'http://127.0.0.1:1453'
session_url = f'{base_url}/0'
# Start the dashboard.
dashboard = Popen(get_python_call('dashboard.py'), cwd='../../../tdw/webgl/dashboard')
sleep(5)
# Create a new session.
post(f'{base_url}/create')
# Start the trial controller.
trial_controller = Popen(get_python_call('dashboard_trial_controller.py'), cwd=getcwd())
# Start the WebGL test server.
webgl_test_server = Popen([executable, 'webgl_test_server.py', '--directory', args.build], cwd='../../')
sleep(3)
# Launch the Build.
open_new_tab('https://localhost:8000')
# Wait a few seconds.
sleep(4)
# Request the trial start time.
post(f'{session_url}/get_trial_start_time')
# Wait a little more.
sleep(8)
print(get(session_url).text)
# Kill all processes.
for process in [dashboard, trial_controller, webgl_test_server]:
    process.terminate()
