from typing import List, Dict, Optional
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback
from tdw.webgl.trials.ninja import Ninja
from tdw.webgl.trials.tabletop import Tabletop
from tdw.webgl.trial_adders.at_end import AtEnd
from tdw.output_data import OutputData, Models, Raycast


class ManyNinjas(TrialController):
    TARGET_OBJECT_NAMES: List[str] = ["bowl", "cone", "cube", "pyramid", "torus"]

    def __init__(self, gravity: float):
        self.gravity: float = gravity
        self.target_object_names = ManyNinjas.TARGET_OBJECT_NAMES[:]
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[Ninja(model_names=ManyNinjas.TARGET_OBJECT_NAMES,
                                          gravity=self.gravity)],
                            adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        # End after the tabletop trial.
        if playback.name == "Tabletop":
            return END_MESSAGE
        if playback.success:
            # Get the names of each model in the scene.
            model_names: Dict[int, str] = dict()
            for resp in playback.frames:
                for i in range(len(resp) - 2):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "mode":
                        models = Models(resp[i])
                        for j in range(models.get_num()):
                            model_names[models.get_id(j)] = models.get_name(j)
                        break
            # Get the ID of the object that was clicked.
            clicked_object_id: Optional[int] = None
            for resp in playback.frames:
                for i in range(len(resp) - 2):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "rayc":
                        raycast = Raycast(resp[i])
                        if raycast.get_hit() and raycast.get_hit_object():
                            clicked_object_id = raycast.get_object_id()
                            break
            # This should never happen.
            if clicked_object_id is None:
                raise Exception("Trial ended in success but no object was clicked.")
            # Get the name of the clicked object.
            clicked_object_name = model_names[clicked_object_id]
            # Remove the clicked object as an object for the target object.
            target_object_names = [name for name in ManyNinjas.TARGET_OBJECT_NAMES if name != clicked_object_name]
            # Return a new trial message.
            return TrialMessage(trials=[Ninja(model_names=target_object_names,
                                              gravity=self.gravity)],
                                adder=AtEnd())
        # Try again, but slow everything down.
        else:
            trials = []
            while self.gravity >= -1:
                self.gravity -= 0.1
                trials.append(Ninja(model_names=self.target_object_names,
                                    gravity=self.gravity))
            # Add a Tabletop at the end.
            trials.append(Tabletop())
            return TrialMessage(trials=trials, adder=AtEnd())
