from typing import List, Union
from pathlib import Path
from json import loads
import importlib
from tdw.controller import Controller
from tdw.add_ons.trials.trial import Trial
from tdw.add_ons.trials.trial_status import TrialStatus
from pkg_resources import resource_filename


class TrialController(Controller):
    def __init__(self,  port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # A sequential list of trials.
        self._trials: List[Trial] = list()

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        # Initialize the next trial.
        if not self._trials[0].initialized:
            # Insert early initialization commands.
            for command in self._trials[0].get_early_initialization_commands():
                commands.insert(0, command)
            # Append initialization commands.
            commands.extend(self._trials[0].get_initialization_commands())
            # Mark the trial as initialized.
            self._trials[0].initialized = True
        # Get the trial's update commands.
        else:
            commands.extend(self._trials[0].commands[:])
            self._trials[0].commands.clear()

        # Communicate. Get a response.
        resp: List[bytes] = super().communicate(commands=commands)

        # TODO log the commands and resp.

        # Update the current trial.
        self._trials[0].on_send(resp=resp)

        # TODO decide what to do on success/failure.

        # The trial ended.
        if self._trials[0].status != TrialStatus.running:
            # Remove this trial.
            self._trials.pop(0)

        return resp

    def run(self, trials_path: str = "trials.json", quit_on_end: bool = True) -> None:
        # Clear the list of trials.
        self._trials.clear()
        path = Path(trials_path)
        if not path.exists():
            raise Exception("Failed to locate trials.json")
        # Get the default trial types.
        default_trial_types: List[str] = TrialController.get_default_trial_types()
        # Load the trial data.
        trials_data: List[dict] = loads(path.read_text(encoding="utf-8"))
        # Parse each trial.
        for trial_data in trials_data:
            # This is a default trial type.
            if trial_data["$type"] in default_trial_types:
                # Import the module.
                module = importlib.import_module(f"tdw.add_ons.trials.{trial_data['$type']}")
            # Import from somewhere else.
            elif "$import" in trial_data:
                module = importlib.import_module(f"{trial_data['$import']}.{trial_data['$type']}")
            else:
                raise Exception(f"Invalid trial type: {trial_data['$type']}.\n"
                                f"If you want to import a custom trial, be sure to add \"$import\": \"path.to.folder\" "
                                f"to the trial description.")
            # Get the constructor parameters. Ignore type and import specifiers by ignoring the $ prefix.
            constructor_parameters = {k: v for (k, v) in trial_data.items() if k[0] != "$"}
            # Convert the underscore_snake_case filename to an UpperCamelCase class name.
            # Get the class. Create a trial. Add the trial to the list.
            self._trials.append(getattr(module, TrialController.__snake_case_to_camel_case(trial_data["$type"]))(**constructor_parameters))
        # Run each trial.
        while len(self._trials) > 0:
            self.communicate([])
        if quit_on_end:
            self.communicate({"$type": "terminate"})
        
    @staticmethod
    def get_default_trial_types() -> List[str]:
        imports = list()
        for f in Path(resource_filename(__name__, "add_ons/trials")).iterdir():
            module = importlib.import_module(f"tdw.add_ons.trials.{f.stem}")
            # Convert the underscore_snake_case filename to an UpperCamelCase class name.
            att = TrialController.__snake_case_to_camel_case(f.stem)
            # This is probably a TDW file, as opposed to something auto-generated.
            if hasattr(module, att):
                klass = getattr(module, att)
                # This is a trial.
                if klass.__base__.__name__ == "Trial":
                    imports.append(f.stem)
        return imports


    @staticmethod
    def __snake_case_to_camel_case(snake_case: str) -> str:
        """
        :param snake_case: A snake_case string.

        :return: An UpperCamelCase string.
        """

        return snake_case.replace("_", " ").title().replace(" ", "")
