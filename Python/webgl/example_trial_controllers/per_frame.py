from typing import List, Union
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback
from tdw.webgl.trials import Ninja
from tdw.webgl.trial_adders import AtEnd
from tdw.commands.command import Command
from tdw.commands import SetKinematicState
from tdw.output_data import OutputData, ObjectIds, FastTransforms


class PerFrame(TrialController):
    def __init__(self, y: float = 1.1):
        # This is a list of IDs of all objects in the scene. This is set in `on_receive_frame(resp)`.
        self.object_ids: List[int] = list()
        self.kinematic: List[int] = list()
        self.y: float = y
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        # Send a single Ninja trial.
        # Tell the Build to send data per frame.
        return TrialMessage(trials=[Ninja()],
                            adder=AtEnd(),
                            send_data_per_frame=True)

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE

    def on_receive_frame(self, resp: List[bytes]) -> List[Union[Command, dict]]:
        commands = list()
        # Parse the output data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the object IDs.
            if r_id == "obid":
                self.object_ids = ObjectIds(resp[i]).get_ids()
            # Get Fast Transforms data.
            elif r_id == "ftra":
                transforms = FastTransforms(resp[i])
                # Iterate through the known object IDs.
                for j in range(len(self.object_ids)):
                    transform = transforms.get_position(j)
                    # If the object is below the height threshold, make it kinematic.
                    if transform[1] <= self.y and self.object_ids[j] not in self.kinematic:
                        # Append the command.
                        set_kinematic_state = SetKinematicState(id=self.object_ids[j],
                                                                use_gravity=False,
                                                                is_kinematic=True)
                        commands.append(set_kinematic_state)
                        # Mark the object as kinematic.
                        self.kinematic.append(self.object_ids[j])
        return commands


if __name__ == "__main__":
    from tdw.webgl import run
    run(PerFrame())
