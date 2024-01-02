from random import randint
from typing import List
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback
from tdw.webgl.trials.trial import Trial
from tdw.webgl.trials.ninja import Ninja
from tdw.webgl.trial_adders import AtEnd, NoTrials
from tdw.output_data import OutputData, Models


class ManyNinjas(TrialController):
    def __init__(self, initial_min_speed: float = 0.5, initial_max_speed: float = 1.5, acceleration: float = 0.5,
                 num_trials_per_message: int = 5):
        self.min_speed: float = initial_min_speed
        self.max_speed: float = initial_max_speed
        self.acceleration: float = acceleration
        self.num_trials_per_message: int = num_trials_per_message
        self.num_completed: int = 0
        self.any_succeeded: bool = False
        self.model_names: List[str] = ["bowl", "cone", "cube", "pyramid", "torus"]
        self.target_object_name = "sphere"
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=self._get_trials(), adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        if playback.success:
            self.any_succeeded = True
        self.num_completed += 1
        # Don't send more trials yet.
        if self.num_completed < self.num_trials_per_message:
            return TrialMessage(trials=[], adder=NoTrials())
        else:
            self.num_completed = 0
            # At least one trial in the list was a success. Send more trials.
            if self.any_succeeded:
                # Get the target object's model and the other objects' models.
                model_names: List[str] = list()
                target_object_name: str = ""
                for resp in playback.frames:
                    for i in range(len(resp) - 1):
                        r_id = OutputData.get_data_type_id(resp[i])
                        if r_id == "mode":
                            models = Models(resp[i])
                            # The target object is always the first model.
                            target_object_name = models.get_name(0)
                            # Get the names of the other models.
                            for j in range(1, models.get_num()):
                                model_name = models.get_name(j)
                                if target_object_name == model_name:
                                    continue
                                model_names.append(models.get_name(j))
                            break
                # Filter out duplicates.
                self.model_names = list(set(model_names))
                # Get a random new target object.
                target_object_name_index = randint(0, len(self.model_names) - 1)
                self.target_object_name = self.model_names[target_object_name_index]
                # Remove the new target object.
                del self.model_names[target_object_name_index]
                # Append the old target object name.
                self.model_names.append(target_object_name)
                # Get new trials.
                return TrialMessage(trials=self._get_trials(), adder=AtEnd())
            # There were no successful trials. End now.
            else:
                return END_MESSAGE

    def _get_trials(self) -> List[Trial]:
        trials = [Ninja(model_names=self.model_names,
                        target_object_names=[self.target_object_name],
                        speed_range=[self.min_speed, self.max_speed]) for _ in range(self.num_trials_per_message)]
        # Accelerate for the next message.
        self.min_speed += self.acceleration
        self.max_speed += self.acceleration
        return trials


if __name__ == "__main__":
    from tdw.webgl import run
    run(ManyNinjas())
