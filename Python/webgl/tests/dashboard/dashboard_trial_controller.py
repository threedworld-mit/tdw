from tdw.webgl import TrialController, TrialMessage, TrialPlayback, END_MESSAGE, run
from tdw.webgl.trial_adders import AtEnd
from tdw.webgl.trials import Ninja


class DashboardTrialController(TrialController):
    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[Ninja(time=10)], adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE


def run_trial_controller():
    run(DashboardTrialController())
