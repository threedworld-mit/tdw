from requests import post, get
from tdw.webgl import TrialController, TrialMessage, TrialPlayback, END_MESSAGE, run
from tdw.webgl.trial_adders import AtEnd
from tdw.webgl.trials import Ninja


base_url = 'http://127.0.0.1:1453'


class DashboardTrialController(TrialController):
    def get_initial_message(self) -> TrialMessage:
        resp = post(f'{base_url}/create')
        assert resp.status_code == 200, resp.status_code
        assert resp.text == '0', resp.text
        # Send a request.
        resp = post(f'{base_url}/0/get_trial_name')
        assert resp.status_code == 200, resp.status_code
        assert resp.text == 'ok', resp.text
        return TrialMessage(trials=[Ninja(scene_name="reference_task_room")], adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        print(get(f'{base_url}/0').text)
        return END_MESSAGE


if __name__ == "__main__":
    d = DashboardTrialController()
    run(d, session_id=0)
