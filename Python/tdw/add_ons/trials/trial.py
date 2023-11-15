from abc import ABC, abstractmethod
from typing import final, List
from tdw.add_ons.ui_widgets.loading_screen import LoadingScreen
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.trials.trial_status import TrialStatus


class Trial(AddOn, ABC):
    def __init__(self):
        super().__init__()
        # Get the add-ons.
        self._add_ons: List[AddOn] = self._get_add_ons()
        # Insert a loading screen.
        self._add_ons.insert(0, LoadingScreen())
        """:field
        The current state of this trial.
        """
        self.status: TrialStatus = TrialStatus.uninitialized

    @final
    def get_initialization_commands(self) -> List[dict]:
        commands = []
        # Insert early initialization commands at the start of the list.
        for i in range(len(self._add_ons)):
            commands.extend(self._add_ons[i].get_early_initialization_commands())
        # Get trial-specific initialization commands.
        commands.extend(self._get_trial_initialization_commands())
        # Initialize the add-ons.
        for i in range(len(self._add_ons)):
            self._add_ons[i].initialized = True
            commands.extend(self._add_ons[i].get_initialization_commands())
        return commands

    @final
    def on_send(self, resp: List[bytes]) -> None:
        # Don't do anything if the trial is done.
        if self.status != TrialStatus.running:
            return

        # Trial-specific early update.
        self._update_trial(resp=resp)

        # Update the add-ons and append commands.
        for i in range(len(self._add_ons)):
            # Manually clear the previous list of commands.
            self._add_ons[i].commands.clear()
            # Update the add-on. This may append commands to its `self.commands`.
            self._add_ons[i].on_send(resp=resp)
            # Append the add-on's commands to the trial's.
            self.commands.extend(self._add_ons[i].commands)

        # Update the trial's status.
        self.status = self._get_trial_status(resp=resp)

    @abstractmethod
    def _get_instructions(self) -> str:
        """
        :return: Instructions text for the loading screen.
        """

        raise Exception()

    @abstractmethod
    def _get_add_ons(self) -> List[AddOn]:
        """
        :return: A list of add-ons.
        """

        raise Exception()

    @abstractmethod
    def _get_trial_initialization_commands(self) -> List[dict]:
        """
        :return: A list of commands to initialize this trial.
        """

        raise Exception()

    @abstractmethod
    def _update_trial(self, resp: List[bytes]) -> None:
        """
        This is executed every time `add_on.on_send(resp)` is called.

        :param resp: The response from the build.
        """

        raise Exception()

    @abstractmethod
    def _get_trial_status(self, resp: List[bytes]) -> TrialStatus:
        """
        :param resp: The response from the build.

        :return: The status of the trial after it finishes updating.
        """

        raise Exception()
