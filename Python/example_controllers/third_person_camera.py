from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.camera.camera import Camera
from tdw.camera.move_target import MoveTarget
from tdw.camera.rotate_target import RotateTarget
from tdw.camera.focus_target import FocusTarget


class ThirdPersonCamera(Controller):
    def run(self) -> None:
        self.start()

        avatar_id = "c"
        cam = Camera(avatar_id=avatar_id)
        object_id = 0
        commands = [{"$type": "set_target_framerate",
                     "framerate": 60},
                    {"$type": "load_scene", "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12),
                    self.get_add_object(model_name="iron_box",
                                        object_id=object_id,
                                        position={"x": 0, "y": 0, "z": 0.5})]
        # Set a teleport and look at target, rotation, and focus.
        cam.move_target = MoveTarget(avatar_id="c",
                                     target={"x": -3, "y": 2, "z": 0})
        cam.rotate_target = RotateTarget(avatar_id="c",
                                         target={"r": 0, "p": 70, "y": -120},
                                         resp=[])
        commands.extend(cam.get_commands([]))
        # Initialize the scene.
        resp = self.communicate(commands)

        # Move the camera towards the object.
        cam.move_target = MoveTarget(avatar_id="c",
                                     target={"x": 1, "y": 1.5, "z": -0.5},
                                     speed=0.1)
        cam.rotate_target = RotateTarget(avatar_id="c",
                                         target=object_id,
                                         centroid=True,
                                         speed=2,
                                         resp=resp)
        cam.focus_target = FocusTarget(avatar_id="c",
                                       target=object_id,
                                       is_object=True,
                                       speed=0.3)
        for i in range(100):
            resp = self.communicate(cam.get_commands(resp=resp))
        # Apply a force to the object.
        commands = [{"$type": "apply_force_to_object",
                     "id": object_id,
                     "force": {"x": 0, "y": 4, "z": 8}}]
        # Move towards the target.
        cam.move_target = MoveTarget(avatar_id="c",
                                     target=object_id,
                                     speed=0.02)
        commands.extend(cam.get_commands(resp=resp))
        self.communicate(commands)
        for i in range(200):
            resp = self.communicate(cam.get_commands(resp=resp))
        # Stop moving the camera.
        cam.move_target = MoveTarget(avatar_id="c")
        # Look away.
        cam.rotate_target = RotateTarget(avatar_id="c",
                                         target={"r": 0, "p": 5, "y": -20},
                                         speed=3,
                                         resp=resp)
        for i in range(100):
            resp = self.communicate(cam.get_commands(resp=resp))

        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ThirdPersonCamera(launch_build=False, udp=False)
    c.run()
