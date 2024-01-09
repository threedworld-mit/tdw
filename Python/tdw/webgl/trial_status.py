# AUTOGENERATED FROM C#. DO NOT MODIFY.

from enum import Enum


class TrialStatus(Enum):
    """
    The status of a trial.
    """

    initializing = 0  # The trial is initializing.
    running = 1  # The trial is still running.
    success = 2  # The trial ended in success.
    failure = 3  # The trial ended in failure.