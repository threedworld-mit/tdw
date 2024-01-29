from time import sleep
from requests import post, get


base_url = 'http://127.0.0.1:1453'
resp = post(f'{base_url}/create')
assert resp.status_code == 200, resp.status_code
assert resp.text == '0', resp.text
resp = post(f'{base_url}/0/get_trial_name')
assert resp.status_code == 200, resp.status_code
assert resp.text == 'ok', resp.text
sleep(2)
print(get(f'{base_url}/0').text)
