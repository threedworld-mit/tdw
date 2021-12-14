from typing import List
from tdw.add_ons.add_on import AddOn


class StepPhysics(AddOn):
    """
    Step n + 1 physics frames per communciate() call.
    """

    def __init__(self, num_frames: int):
        """
        :param num_frames: Step this many physics frames + 1 per communicate() call.
        """

        super().__init__()
        """:field
        Step this many physics frames + 1 per communicate() call.
        """
        self.num_frames: int = num_frames

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        self.commands.append({"$type": "step_physics",
                              "frames": self.num_frames})
