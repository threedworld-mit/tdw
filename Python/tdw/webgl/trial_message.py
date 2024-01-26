# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.webgl.trial_adders.trial_adder import TrialAdder
from tdw.webgl.trials.trial import Trial
from typing import List


class TrialMessage:
    """
    A network message with a new list of trials and a TrialAdder defining where to add them.
    """

    def __init__(self, adder: TrialAdder, trials: List[Trial], send_data_per_frame: bool = False):
        """
        :param adder: Instructions for where to add the new trials in the list of current trials, or to end the simulation.
        :param trials: The new trials. This can be empty.
        :param send_data_per_frame: If true, send output data per-frame and receive commands per-frame. Regardless, you will still receive an end-of-trial message.
        """

        """:field
        The new trials. This can be empty.
        """
        self.trials: List[Trial] = trials
        """:field
        Instructions for where to add the new trials in the list of current trials, or to end the simulation.
        """
        self.adder: TrialAdder = adder
        """:field
        If true, send output data per-frame and receive commands per-frame. Regardless, you will still receive an end-of-trial message.
        """
        self.send_data_per_frame: bool = send_data_per_frame