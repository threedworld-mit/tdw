from json import dumps
from typing import Dict, Union, List
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.collision_manager import CollisionManager
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class CollisionDetection(Controller):
    """
    Vehicle collision detection.
    """

    Z: float = 2.66
    MATERIAL: str = "concrete"
    SCALE: Dict[str, float] = {"x": 0.2, "y": 0.2, "z": 0.4}

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        self.collisions = []
        self.collision_manager = CollisionManager(enter=True, stay=False, exit=False)
        self.vehicle = Vehicle(position={"x": 0, "y": 0, "z": 2.66},
                               rotation={"x": 0, "y": -90, "z": 0},
                               image_capture=False)
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.camera = ThirdPersonCamera(position={"x": 7, "y": 3.5, "z": 1.6},
                                        look_at=self.vehicle.vehicle_id,
                                        follow_object=self.vehicle.vehicle_id,
                                        avatar_id="a")
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vehicle_collision_detection")
        print(f"Images and JSON data will be saved to: {self.path}")
        self.capture = ImageCapture(avatar_ids=["a"], path=self.path)
        self.object_id = Controller.get_unique_id()
        self.add_ons.extend([self.vehicle, self.camera, self.capture, self.collision_manager])

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        # Send the commands.
        resp = super().communicate(commands=commands)
        # Get collisions.
        collisions = []
        for collision in self.collision_manager.obj_collisions:
            if collision.int1 == self.vehicle.vehicle_id:
                collisions.append(collision.int2)
            elif collision.int2 == self.vehicle.vehicle_id:
                collisions.append(collision.int1)
        self.collisions.append(collisions)
        # Return the response from the build.
        return resp

    def run(self):
        # Load the scene.
        commands = [c.get_add_scene(scene_name="suburb_scene_2023")]
        # Add the material.
        commands.extend([Controller.get_add_material(CollisionDetection.MATERIAL)])
        # Add some concrete blocks.
        y = 0
        x = -7
        while y < 5:
            z = 0
            while z < 4.45:
                object_id = Controller.get_unique_id()
                commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                                  object_id=object_id,
                                                                  position={"x": x, "y": y, "z": z},
                                                                  library="models_flex.json",
                                                                  default_physics_values=False,
                                                                  scale_factor=CollisionDetection.SCALE,
                                                                  scale_mass=False,
                                                                  mass=4))
                # Set the visual material.
                commands.append({"$type": "set_visual_material",
                                 "material_index": 0,
                                 "material_name": CollisionDetection.MATERIAL,
                                 "object_name": "cube",
                                 "id": object_id})
                z += CollisionDetection.SCALE["z"]
            y += CollisionDetection.SCALE["y"]
        # Send the commands.
        self.communicate(commands)
        # Drive.
        self.move_by(10)
        # Quit.
        self.communicate({"$type": "terminate"})
        # Save the collision data.
        self.path.joinpath("collisions.json").write_text(dumps(self.collisions))

    def move_by(self, distance: float):
        # Get the initial position.
        p0: np.ndarray = np.copy(self.vehicle.dynamic.transform.position)
        self.vehicle.set_drive(1)
        # Drive until the vehicle exceeds the distance.
        while np.linalg.norm(p0 - self.vehicle.dynamic.transform.position) < distance:
            self.communicate([])
        # Brake until the vehicle stops moving.
        self.vehicle.set_drive(0)
        self.vehicle.set_brake(1)
        while np.linalg.norm(self.vehicle.dynamic.rigidbody.velocity) > 0.01:
            self.communicate([])


if __name__ == "__main__":
    c = CollisionDetection()
    c.run()
