from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.replicant.action_status import ActionStatus


class CollisionDetectionTests(Controller):
    """
    Test Replicant collision detection.
    """

    OBJECT_ID: int = 1

    def test(self, status: ActionStatus, kinematic: bool = False, avoid: bool = True,
             exclude: bool = False, distance: float = 4) -> None:
        """
        Test collision detection.

        :param status: The expected action status at the end of the move_by(distance) action.
        :param kinematic: If True, the object is kinematic.
        :param avoid: If True, try to avoid obstacles and walls.
        :param exclude: If True, ignore collisions with the object.
        :param distance: The distance to move by.
        """

        self.add_ons.clear()
        replicant = Replicant()
        camera = ThirdPersonCamera(position={"x": 2, "y": 3, "z": 0.3},
                                   look_at=replicant.replicant_id)
        self.add_ons.extend([replicant, camera])
        replicant.collision_detection.avoid = avoid
        if exclude:
            replicant.collision_detection.exclude_objects.append(CollisionDetectionTests.OBJECT_ID)
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        commands.extend(Controller.get_add_physics_object(model_name="trunck",
                                                          object_id=CollisionDetectionTests.OBJECT_ID,
                                                          position={"x": 0, "y": 0, "z": 3},
                                                          kinematic=kinematic))
        self.communicate(commands)
        replicant.move_by(distance)
        while replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        assert replicant.action.status == status, replicant.action.status


if __name__ == "__main__":
    c = CollisionDetectionTests()
    c.test(status=ActionStatus.detected_obstacle)
    c.test(avoid=False, status=ActionStatus.collision)
    c.test(avoid=False, exclude=True, status=ActionStatus.success)
    c.test(distance=-12, status=ActionStatus.detected_obstacle)
    c.test(kinematic=True, status=ActionStatus.detected_obstacle)
    c.test(kinematic=True, avoid=False, status=ActionStatus.collision)
    c.communicate({"$type": "terminate"})
