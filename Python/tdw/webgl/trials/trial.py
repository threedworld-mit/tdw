# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.webgl.trial_status import TrialStatus


class Trial(ABC):
    """
    Abstract base class for a trial.
    """

    def __init__(self, framerate: int = 60, render_quality: int = 5):
        """
        :param framerate: The target framerate.
        :param render_quality: The render quality (0 to 5, where 5 is best).
        """

        """:field
        The target framerate.
        """
        self.framerate: int = framerate
        """:field
        The render quality (0 to 5, where 5 is best).
        """
        self.render_quality: int = render_quality
        """:field
        The state of this trial.
        """
        self.status: TrialStatus = TrialStatus.initializing
