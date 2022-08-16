from typing import Dict, List


class ReplicantStatic():
    """
    Static data for the Magnebot.

    With a [`Magnebot` agent](magnebot.md):

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from magnebot.magnebot import Magnebot

    m = Magnebot(robot_id=0, position={"x": 0.5, "y": 0, "z": -1})
    c = Controller()
    c.add_ons.append(m)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    for magnet in m.static.magnets:
        magnet_id = m.static.magnets[magnet]
        print(magnet, magnet_id)
    c.communicate({"$type": "terminate"})
    ```

    With a single-agent [`MagnebotController`](magnebot_controller.md):

    ```python
    from magnebot import MagnebotController

    m = MagnebotController()
    m.init_scene()
    for magnet in m.magnebot.static.magnets:
        magnet_id = m.magnebot.static.magnets[magnet]
        print(magnet, magnet_id)
    m.end()
    ```
    """

    def __init__(self, replicant_id: int, resp: List[bytes]):
        """:field
        The ID of the replicant.
        """
        self.replicant_id: int = replicant_id
        """:field
        A dictionary of body parts. Key = The part ID. Value = The name of the part.
        """
        self.joints: Dict[int,str] = dict()
        """:field
        The name and ID of each arm joint. Key = The [`ArmJoint` enum value](arm_joint.md). Value = The object ID.
        """
        self.arm_joints: Dict[ArmJoint, int] = dict()
        """:field
        A list of joint IDs.
        """
        self.body_parts: List[int] = list()
        """:field
        The ID of the Magnebot's avatar (camera). This is used internally for API calls.
        """
        self.avatar_id: str = str(replicant_id)

        self.body_parts: List[int] = list(self.joints.keys())
