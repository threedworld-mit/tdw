from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus


class CollisionDetectionTests(Controller):
    OBJECT_ID: int = 1

    def test(self, status: ActionStatus, kinematic: bool = False, walls: bool = True, avoid: bool = True,
             exclude: bool = False, distance: float = 4) -> None:
        """
        Initialize the scene.

        :param kinematic: If True, the trunk is kinematic.
        """

        self.add_ons.clear()
        r = Replicant()
        self.add_ons.append(r)
        r.collision_detection.walls = walls
        r.collision_detection.avoid = avoid
        if exclude:
            r.collision_detection.exclude_objects.append(CollisionDetectionTests.OBJECT_ID)
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        commands.extend(Controller.get_add_physics_object(model_name="trunck",
                                                          object_id=CollisionDetectionTests.OBJECT_ID,
                                                          position={"x": 0, "y": 0, "z": 3},
                                                          kinematic=kinematic))
        self.communicate(commands)
        r.move_by(distance)
        while r.action.status == ActionStatus.ongoing:
            self.communicate([])
        assert r.action.status == status, r.action.status


if __name__ == "__main__":
    c = CollisionDetectionTests()
    c.test(kinematic=False, walls=True, status=ActionStatus.detected_obstacle)
    c.communicate({"$type": "terminate"})
