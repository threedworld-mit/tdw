from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.cinematic_camera import CinematicCamera


class ThirdPersonCamera(Controller):
    def run(self) -> None:
        self.start()

        object_id = 0
        commands = [{"$type": "set_target_framerate",
                     "framerate": 60},
                    {"$type": "load_scene", "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12),
                    self.get_add_object(model_name="iron_box",
                                        object_id=object_id,
                                        position={"x": 0, "y": 0, "z": 0.5})]
        # Create a camera object.
        avatar_id = "c"
        cam = CinematicCamera(avatar_id=avatar_id, position={"x": -3, "y": 2, "z": 0},
                              rotation={"x": 0, "y": 34, "z": -120})
        # Add the camera initialization commands.
        commands.extend(cam.init_commands)
        # Initialize the scene.
        resp = self.communicate(commands)

        # Move and rotate towards the object. Focus on the object.
        cam.move_to_object(target=object_id, offset_distance=2, min_y=1.5, centroid=True)
        cam.rotate_to_object(target=object_id, centroid=True)
        cam.focus_on_object(target=object_id, centroid=True)

        for i in range(100):
            resp = self.communicate(cam.get_commands(resp=resp))

        # Move back to center.
        cam.move_to_position(target={"x": 0, "y": 2, "z": 0})
        # Apply a force to the object.
        commands = [{"$type": "apply_force_to_object",
                     "id": object_id,
                     "force": {"x": 0, "y": 4, "z": 8}}]
        commands.extend(cam.get_commands(resp=resp))
        resp = self.communicate(commands)

        for i in range(200):
            resp = self.communicate(cam.get_commands(resp=resp))

        cam.stop_moving()
        # Pan right.
        cam.rotate_by_rpy(target={"x": 0, "y": 45, "z": 0})

        for i in range(100):
            resp = self.communicate(cam.get_commands(resp=resp))

        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ThirdPersonCamera(launch_build=False, udp=False)
    c.run()
