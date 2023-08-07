##### Vehicles

# Vehicles

*Vehicles in TDW are handled via the PhysX physics engine. If you haven't done so already, we strongly recommend you read the [physics tutorial](../physx/physx.md).*

TDW vehicles are agents that drive like cars, trucks, etc.

A vehicle can be added to the scene by using the [`Vehicle`](../../python/add_ons/vehicle.md) add-on:

```python
from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
vehicle = Vehicle(position={"x": 0, "y": 0, "z": 2.66},
                  rotation={"x": 0, "y": -90, "z": 0},
                  image_capture=False)
camera = ThirdPersonCamera(position={"x": 7, "y": 3.5, "z": 1.6},
                           look_at=vehicle.vehicle_id,
                           follow_object=vehicle.vehicle_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vehicle_suburb")
capture = ImageCapture(avatar_ids=["a"], path=path)
print(f"Images will be saved to: {path}")
c.add_ons.extend([vehicle, camera, capture])
c.add_ons.extend([vehicle, camera])
c.communicate([c.get_add_scene(scene_name="suburb_scene_2023")])
for i in range(50):
    c.communicate([])
# Drive up the street.
vehicle.set_drive(1)
for i in range(160):
    c.communicate([])
# Slow down.
vehicle.set_drive(0.2)
vehicle.set_brake(0.2)
for i in range(40):
    c.communicate([])
# Turn into the driveway.
vehicle.set_brake(0)
vehicle.set_turn(1)
vehicle.set_drive(0)
for i in range(150):
    c.communicate([])
# Hit the brakes.
vehicle.set_turn(0)
vehicle.set_brake(0.5)
for i in range(50):
    c.communicate([])
c.communicate({"$type": "terminate"})

```

Result:

![](images/minimal.gif)

## Drive, turn, and brake

You can set the vehicle's drive, turn, and brake via `vehicle.set_drive(value)`, `vehicle.set_turn(value)`, and `vehicle.set_brake(value)`. Each `value` is a float clamped between -1.0 and 1.0. Setting the value does *not* instantaneously set the vehicle's speed or turn angle; rather, the values affect the acceleration, turn rate, and deceleration, respectively.

## Initial position and rotation

To set the vehicle's initial position and rotation, set the `position` and `rotation` parameters in the constructor, for example: `vehicle = Vehicle(position={"x": 1, "y": 0, "z": 0}, rotation={"x": 0, "y": -90, "z": 0})`.

## Set optional speed parameters

You can control the maximum speed of a vehicle by setting `forward_speed` and `maximum_speed` in the constructor, for example: `vehicle = Vehicle(forward_speed=60)`.

For more information, [read the API documentation](../../python/add_ons/vehicle.md).

## Output data and images

The vehicle stores its output data in `vehicle.dynamic`, which is a [`VehicleDynamic`](../../python/vehicle/vehicle_dynamic.md) data object. This data includes the vehicle's transform data, rigidbody data, and image data.

Transform data is stored as a [`Transform`](../../python/object_data/transform.md): `vehicle.dynamic.transform`. 

Rigidbody data includes the vehicle's directional and angular speed. It is stored as a [`Rigidbody`](../../python/object_data/rigidbody.md): `vehicle.dynamic.rigidbody`.

Images are stored in a dictionary: `vehicle.dynamic.images`. The key is a string indicating the capture pass, for example `"_img"`. 

By default, the vehicle saves [RGB images](../core_concepts/images.md) and [depth maps](../visual_perception/depth.md). To set the vehicle's image passes, set the optional `image_passes` parameter in the constructor like this: `vehicle = Vehicle(image_passes=["_img"])`. 

The vehicle's camera matrices are stored in `vehicle.dynamic.camera_matrix` and `vehicle.dynamic.projection_matrix`.

To disable image capture, set the optional `image_capture` parameter in the constructor to False: `vehicle = Vehicle(image_capture=False)`. As with any camera in TDW, disabling image capture will allow the camera to continue to render to the window even though it isn't returning image data.

Note that, as with any camera, an [`ImageCapture`](../core_concepts/images.md) add-on, which most of these examples include, can supersede the vehicle's image capture parameters, depending on the order in which the add-ons are appended to `c.add_ons`.

To save images, you can call `vehicle.dynamic.save_images(output_directory)`. To convert the raw image data to a PIL image, call `vehicle.dynamic.get_pil_image(pass_mask)`.

In this example, we'll drive the vehicle and record its data every communicate() call. This is an unusual controller because it overrides `communicate()` in order to save vehicle images and record the vehicle's transform and rigidbody per call:

```python
from json import dumps
from typing import Union, List
from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class DynamicData(Controller):
    """
    Read and save the vehicle's output data, including image data.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        self._first_time_only = True
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vehicle = Vehicle(rotation={"x": 0, "y": -90, "z": 0}, image_passes=["_img"])
        self.add_ons.append(self.vehicle)
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vehicle_dynamic_data")
        print(f"Images and JSON data will be saved to: {self.path}")
        # Start the json data.
        self.output_data = list()

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        resp = super().communicate(commands=commands)
        if self._first_time_only:
            self._first_time_only = False
            return resp
        # Save the vehicle's images.
        self.vehicle.dynamic.save_images(output_directory=self.path)
        # Write the other data as a JSON file.
        output_data = {"transform": {"position": self.vehicle.dynamic.transform.position.tolist(),
                                     "rotation": self.vehicle.dynamic.transform.rotation.tolist(),
                                     "forward": self.vehicle.dynamic.transform.forward.tolist()},
                       "rigidbody": {"velocity": self.vehicle.dynamic.rigidbody.velocity.tolist(),
                                     "angular_velocity": self.vehicle.dynamic.rigidbody.angular_velocity.tolist()},
                       "camera_matrices": {"camera_matrix": self.vehicle.dynamic.camera_matrix.tolist(),
                                           "projection_matrix": self.vehicle.dynamic.projection_matrix.tolist()}}
        # Remember the output data.
        self.output_data.append(output_data)
        # Return the response from the build.
        return resp

    def run(self):
        self.communicate(c.get_add_scene(scene_name="suburb_scene_2023"))
        # Drive the vehicle forward.
        self.vehicle.set_drive(0.5)
        while self.vehicle.dynamic.transform.position[0] > -30:
            self.communicate([])
        # Brake.
        self.vehicle.set_drive(0)
        self.vehicle.set_brake(0.7)
        for i in range(100):
            c.communicate([])
        # Quit.
        self.communicate({"$type": "terminate"})
        # Write the JSON data.
        self.path.joinpath("output_data.json").write_text(dumps(self.output_data, indent=2))


if __name__ == "__main__":
    c = DynamicData()
    c.run()
```

Result:

![](images/dynamic_data.gif)

This will also write data to a JSON file.

## Wrap vehicle movement in functions

So far, the examples in this document have waited a certain number of communicate() calls to drive a vehicle. In some use-cases, you will want to wait until the vehicle has driven a certain distance, reached a certain speed, etc.

This controller wraps `vehicle.set_drive(force)` in a simple `move_by(distance)` function that calls communicate() until the vehicle is at a target distance:

```python
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MoveBy(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vehicle = Vehicle(rotation={"x": 0, "y": -90, "z": 0}, image_passes=["_img"])
        self.add_ons.append(self.vehicle)
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vehicle_dynamic_data")

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
        print(np.linalg.norm(p0 - self.vehicle.dynamic.transform.position))

    def run(self):
        self.communicate(c.get_add_scene(scene_name="suburb_scene_2023"))
        self.move_by(6)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = MoveBy()
    c.run()
```

Many improvements could be made to this example. Most importantly, the `move_by(distance)` function will always overshoot by up to several meters. This is because braking is not instantaneous. Just like driving a real vehicle, this would work better if the vehicle drives to a shorter distance than the target and brakes until it is at `distance`.

## Collision detection

The vehicle is technically a subclass of a standard [TDW object](../core_concepts/objects.md) and therefore will appear in object output data, including collision output data. 

You can use a [`CollisionManager`](../physx/collisions.md) to listen for collisions between the vehicle and other objects like this:

```python
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
```

Result:

![](images/collision_detection.gif)

This will also write a list of IDs per frame that the vehicle collided with to a JSON file.

## Physical realism

**Vehicles are *not* entirely physically realistic.** 

Vehicles *are* realistic in that they look like vehicles and respond to [PhysX forces](../physx/forces.md). Whenever you set the vehicle's drive, turn, or brake values,  you are adjusting forces being applied to it per communicate() call. As explained above, vehicles can collide with objects.

However, TDW doesn't include a true driving simulation.  TDW does not attempt to model individual parts of vehicles, realistic tires, fuel consumption, etc.

## Low-level description

The vehicle is added to the scene via [`add_vehicle`](../../api/command_api.md#add_vehicle).  And [avatar](../core_concepts/avatars.md) is attached to the vehicle via [`create_avatar`](../../api/command_api.md#create_avatar) and [`parent_avatar_to_vehicle`](../../api/command_api.md#parent_avatar_to_vehicle).

Per communicate call, the vehicle receives [`Transforms`](../../api/output_data.md#Transforms) and  [`Rigidbodies`](../../api/output_data.md#Rigidbodies) output data.

The vehicle's drive, brake, and turn are set by continuously sending [`apply_vehicle_drive`](../../api/command_api.md#apply_vehicle_drive), [`apply_vehicle_brake`](../../api/command_api.md#apply_vehicle_brake), and [`apply_vehicle_turn`](../../api/command_api.md#apply_vehicle_turn), respectively. The vehicle's motor is set via [`set_vehicle_motor`](../../api/command_api.md#set_vehicle_motor).

***

**This is the last document in the "Vehicle" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vehicle/minimal.py) Minimal example of a vehicle driving in a suburb.
- [collision_detection.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vehicle/collision_detection.py) Vehicle collision detection.
- [dynamic_data.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vehicle/dynamic_data.py) Read and save the vehicle's output data, including image data.
- [move_by.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vehicle/move_by.py) Wrap vehicle movement in a simple "move by" function.

Python API:

- [`Vehicle`](../../python/add_ons/vehicle.md)
- [`VehicleDynamic`](../../python/vehicle/vehicle_dynamic.md)
- [`Transform`](../../python/object_data/transform.md)
- [`Rigidbody`](../../python/object_data/rigidbody.md)

Command API:

- [`add_vehicle`](../../api/command_api.md#add_vehicle)
- [`create_avatar`](../../api/command_api.md#create_avatar)
- [`parent_avatar_to_vehicle`](../../api/command_api.md#parent_avatar_to_vehicle)
- [`apply_vehicle_drive`](../../api/command_api.md#apply_vehicle_drive)
- [`apply_vehicle_brake`](../../api/command_api.md#apply_vehicle_brake)
- [`apply_vehicle_turn`](../../api/command_api.md#apply_vehicle_turn)

Output Data:

-  [`Transforms`](../../api/output_data.md#Transforms)
-  [`Rigidbodies`](../../api/output_data.md#Rigidbodies)