import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.embodied_avatar import EmbodiedAvatar

"""
Move an embodied avatar by a given distance.
"""


class MoveBy(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.embodied_avatar: EmbodiedAvatar = EmbodiedAvatar()
        self.add_ons.append(self.embodied_avatar)

    def move_by(self, distance: float, force: float) -> float:
        p_0 = np.array(self.embodied_avatar.transform.position[:])
        self.embodied_avatar.apply_force(force)
        # Wait until the avatar has nearly finished moving.
        while self.embodied_avatar.is_moving and np.linalg.norm(self.embodied_avatar.transform.position - p_0) < distance - 0.015:
            c.communicate([])
        # Stop the avatar.
        self.embodied_avatar.set_drag(drag=80, angular_drag=100)
        while self.embodied_avatar.is_moving:
            c.communicate([])
        # Reset the drag.
        self.embodied_avatar.set_drag()
        # Return the distance traveled.
        return np.linalg.norm(self.embodied_avatar.transform.position - p_0)

    def run(self) -> None:
        # Create a scene. This will also add the embodied avatar.
        self.communicate(TDWUtils.create_empty_room(12, 12))
        for distance, force in zip([0.5, 1.5], [500, 500]):
            actual_distance = self.move_by(distance=distance, force=force)
            print("Target distance:", distance)
            print("Actual distance:", actual_distance)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = MoveBy()
    c.run()
