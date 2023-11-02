from abc import ABC, abstractmethod
from typing import final, List
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.trials.trial_status import TrialStatus


class Trial(AddOn, ABC):
    def __init__(self):
        super().__init__()
        self._add_ons_early: List[AddOn] = self._get_add_ons_early()
        self._add_ons_late: List[AddOn] = self._get_add_ons_late()
        self.status: TrialStatus = TrialStatus.running

    @final
    def get_initialization_commands(self) -> List[dict]:
        commands = []
        # Initialize the early add-ons.
        self.__initialize_add_ons(commands=commands, add_ons=self._add_ons_early)
        # Get early trial-specific initialization commands.
        commands.extend(self._get_trial_initialization_commands_early())
        # Initialize the late add-ons.
        self.__initialize_add_ons(commands=commands, add_ons=self._add_ons_late)
        # Get late trial-specific initialization commands.
        commands.extend(self._get_trial_initialization_commands_late())
        return commands

    @final
    def on_send(self, resp: List[bytes]) -> None:
        # Don't do anything if the trial is done.
        if self.status != TrialStatus.running:
            return
        # Update the early add-ons.
        self.__update_add_ons(resp=resp, add_ons=self._add_ons_early)
        # Trial-specific early update.
        self._on_send_early(resp=resp)
        # Update the late add-ons.
        self.__update_add_ons(resp=resp, add_ons=self._add_ons_late)
        # Trial-specific late update.
        self._on_send_late(resp=resp)
        # Update the trial's status.
        self.status = self._get_trial_status(resp=resp)

    @abstractmethod
    def _get_add_ons_early(self) -> List[AddOn]:
        """
        :return: A list of add-ons that will inject commands before anything else.
        """

        raise Exception()

    @abstractmethod
    def _get_add_ons_late(self) -> List[AddOn]:
        """
        :return: A list of add-ons that will inject commands after the early add-ons and after the early trial commands.
        """

        raise Exception()

    @abstractmethod
    def _get_trial_initialization_commands_early(self) -> List[dict]:
        """
        :return: A list of commands to initialize this trial. These commands are added after adding the early add-ons' commands.
        """

        raise Exception()

    @abstractmethod
    def _get_trial_initialization_commands_late(self) -> List[dict]:
        """
        :return: A list of commands to initialize this trial. These commands are added after adding the late add-ons' commands.
        """

        raise Exception()

    @abstractmethod
    def _on_send_early(self, resp: List[bytes]) -> None:
        """
        The early on_send step. This is executed after the early add-ons' on_send().

        :param resp: The response from the build.
        """

        raise Exception()

    @abstractmethod
    def _on_send_late(self, resp: List[bytes]) -> None:
        """
        The late on_send step. This is executed after the late add-ons' on_send().

        :param resp: The response from the build.
        """

        raise Exception()

    def _get_trial_status(self, resp: List[bytes]) -> TrialStatus:
        """
        :param resp: The response from the build.

        :return: A new trial status. This is executed after all early/late trial/add-on update calls, within on_send().
        """

        raise Exception()

    @staticmethod
    def __initialize_add_ons(commands: List[dict], add_ons: List[AddOn]) -> None:
        """
        Initialize a list of add-ons.

        :param commands: The initialization commands. Each add-on will add to this list.
        :param add_ons: The add-ons.
        """

        for i in range(len(add_ons)):
            add_ons[i].initialized = True
            commands.extend(add_ons[i].get_initialization_commands())

    def __update_add_ons(self, resp: List[bytes], add_ons: List[AddOn]) -> None:
        """
        Update a list of add-ons within the trial's on_send().

        :param resp: The response from the build.
        :param add_ons: The add-ons.
        """

        for i in range(len(add_ons)):
            # Manually clear the previous list of commands.
            add_ons[i].commands.clear()
            # Update the add-on. This may append commands to its `self.commands`.
            add_ons[i].on_send(resp=resp)
            # Append the add-on's commands to the trial's.
            self.commands.extend(add_ons[i].commands)
