from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.cinematic_camera import CinematicCamera
from tdw.add_ons.image_capture import ImageCapture


class CinematicCameraController(Controller):
    def run(self) -> None:
        object_id = 0
        self.start()
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          self.get_add_object(model_name="iron_box", object_id=object_id)])

        # Create a cinematic camera.
        camera = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                                 rotation={"x": 2, "y": 45, "z": 0})
        # Save images per frame.
        capture = ImageCapture(path="D:/cinematic_camera_controller",
                               avatar_ids=[camera.avatar_id])
        # Add the add-ons to the controller.
        self.add_ons.extend([camera, capture])

        # Look at the target object.
        camera.move_to_object(target=object_id, offset_distance=1)
        camera.rotate_to_object(target=object_id)
        done = False
        while not done:
            resp = self.communicate([])
            motions = camera.motions_are_done(resp=resp)
            done = motions["move"] and motions["rotate"]
        # Move away from the target object.
        camera.move_to_position(target={"x": 0, "y": 0, "z": -5}, relative=True)
        camera.rotate_by_rpy(target={"x": 0, "y": -20, "z": 0})
        done = False
        while not done:
            resp = self.communicate([])
            motions = camera.motions_are_done(resp=resp)
            done = motions["move"] and motions["rotate"]
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = CinematicCameraController(launch_build=False)
    c.run()
