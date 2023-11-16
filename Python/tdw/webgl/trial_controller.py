from argparse import ArgumentParser
from json import loads
from importlib import import_module
import pkgutil
from typing import List, Tuple, final
from tdw.webgl.webgl_controller import WebGLController, run
from tdw.add_ons.trials.trial import Trial
from tdw.add_ons.trials.trial_status import TrialStatus
from tdw.type_aliases import PATH
from tdw.tdw_utils import TDWUtils


class TrialController(WebGLController):
    def __init__(self, port: int = 1071, check_version: bool = True):
        """
        :param port: The port number.
        :param check_version: If True, check if an update is available on PyPi and print the result.
        """

        super().__init__(port=port, check_version=check_version)
        self._trials: List[Trial] = list()

    @final
    def load_trials(self, path: PATH = "trials.json", clear: bool = True) -> None:
        if clear:
            self._trials.clear()
        trial_path = TDWUtils.get_path(path=path)
        if not trial_path.exists():
            raise Exception("Path does not exist: " + str(trial_path.resolve()))
        # Load the trial data.
        trials_data: List[dict] = loads(trial_path.read_text(encoding="utf-8"))
        # Parse each trial.
        for trial_data in trials_data:
            # This is a default trial type.
            if trial_data["$type"] in DEFAULT_TRIAL_TYPES:
                # Import the module.
                module = import_module(f"tdw.add_ons.trials.{trial_data['$type']}")
            # Import from somewhere else.
            elif "$import" in trial_data:
                module = import_module(f"{trial_data['$import']}.{trial_data['$type']}")
            else:
                raise Exception(f"Invalid trial type: {trial_data['$type']}.\n"
                                f"If you want to import a custom trial, be sure to add \"$import\": \"the.import.path\" "
                                f"to the trial description.")
            # Get the constructor parameters. Ignore type and import specifiers by ignoring the $ prefix.
            constructor_parameters = {k: v for (k, v) in trial_data.items() if k[0] != "$"}
            # Convert the underscore_snake_case filename to an UpperCamelCase class name.
            # Get the class. Create a trial. Add the trial to the list.
            self._trials.append(getattr(module, _snake_to_camel(trial_data["$type"]))(**constructor_parameters))

    @final
    def on_communicate(self, resp: List[bytes]) -> Tuple[bool, List[dict]]:
        # TODO logging.
        if len(self._trials) > 0:
            status: TrialStatus = self._trials[0].status
            # Initialize the trial.
            if status == TrialStatus.uninitialized:
                self._trials[0].status = TrialStatus.running
                commands = self._trials[0].get_early_initialization_commands()
                commands.extend(self._trials[0].get_initialization_commands())
                return False, commands
            # Update the trial.
            elif status == TrialStatus.running:
                self._trials[0].commands.clear()
                self._trials[0].on_send(resp=resp)
                return False, self._trials[0].commands
            else:
                print(self._trials[0].status)
                # TODO do something on success/failure.
                self._trials.pop(0)
                return False, []
        else:
            return True, []


def get_default_trial_types() -> List[str]:
    imports = list()
    # Source: https://stackoverflow.com/a/43059528
    module = import_module("tdw.add_ons.trials")
    # Source: https://stackoverflow.com/a/48962311
    for importer, name, ispkg in pkgutil.iter_modules(module.__path__):
        if not ispkg:
            module = import_module(f"tdw.add_ons.trials.{name}")
            # Convert the underscore_snake_case filename to an UpperCamelCase class name.
            att = _snake_to_camel(name)
            # This is probably a TDW file, as opposed to something auto-generated.
            if hasattr(module, att):
                klass = getattr(module, att)
                # This is a trial.
                if klass.__base__.__name__ == "Trial":
                    imports.append(name)
    return imports


def launch() -> None:
    """
    Launch a TrialController and serve indefinitely.
    """

    parser = ArgumentParser()
    parser.add_argument("port", type=int, help="The WebSocket port.")
    parser.add_argument("trials_path", type=str, help="The path to trials.json")
    args, unknown = parser.parse_known_args()
    tc = TrialController(port=args.port)
    tc.load_trials(path=args.trials_path)
    run(tc)


def _snake_to_camel(snake_case: str) -> str:
    """
    :param snake_case: A snake_case string.

    :return: An UpperCamelCase string.
    """

    return snake_case.replace("_", " ").title().replace(" ", "")


DEFAULT_TRIAL_TYPES: List[str] = get_default_trial_types()
