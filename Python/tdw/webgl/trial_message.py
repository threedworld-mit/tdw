# AUTOGENERATED FROM C#. DO NOT MODIFY.

from typing import List
from tdw.webgl.trials.trial import Trial
from tdw.webgl.trial_adders.trial_adder import TrialAdder


class TrialMessage:
    """
    A network message with a new list of trials and a TrialAdder defining where to add them.
    """

    def __init__(self, adder: TrialAdder, trials: List[Trial], send_data_per_trial: bool = True):
        """
        :param adder: Instructions for where to add the new trials in the list of current trials, or to end the simulation.
        :param trials: The new trials. This can be empty.
        :param send_data_per_trial: If true, send output data at the end of a trial. If false, send output data per-frame and receive commands per-frame.
        """

        if trials is None:
            """:field
            The new trials. This can be empty.
            """
            self.trials: List[Trial] = list()
        else:
            self.trials = trials
        """:field
        Instructions for where to add the new trials in the list of current trials, or to end the simulation.
        """
        self.adder: TrialAdder = adder
        """:field
        If true, send output data at the end of a trial. If false, send output data per-frame and receive commands per-frame.
        """
        self.send_data_per_trial: bool = send_data_per_trial
