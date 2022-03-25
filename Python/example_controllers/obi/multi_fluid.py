from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.obi_data.fluids.cube_emitter import CubeEmitter
from tdw.obi_data.fluids.disk_emitter import DiskEmitter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add two fluid emitters to the scene.
Use position markers to demonstrate that the particle output data matches the rendered geometry.
"""

fluid = "water"
c = Controller(launch_build=False)
# Add a camera.
camera = ThirdPersonCamera(position={"x": 3, "y": 6, "z": -1.5},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
# Enable image capture.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_fluid")
print(f"Images will be saved to: {path}")
image_capture = ImageCapture(avatar_ids=["a"], pass_masks=["_img"], path=path)
# Add Obi.
obi = Obi()
c.add_ons.extend([camera, image_capture, obi])
# Create two fluids.
obi.create_fluid(object_id=Controller.get_unique_id(),
                 fluid=fluid,
                 position={"x": 0, "y": 2.35, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 shape=CubeEmitter(size={"x": 0.5, "y": 0.5, "z": 0.5}),
                 speed=1)
obi.create_fluid(object_id=Controller.get_unique_id(),
                 fluid=fluid,
                 position={"x": 2, "y": 1.5, "z": -2},
                 rotation={"x": 0.45, "y": 0, "z": 0},
                 shape=DiskEmitter(radius=0.5),
                 speed=1.5)
# Create the scene. Initialize Obi. Add the fluids.
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(100):
    # Use position markers to show where the particles are.
    commands = [{"$type": "remove_position_markers"}]
    for actor_id in obi.actors:
        for position in obi.actors[actor_id].positions:
            commands.append({"$type": "add_position_marker",
                             "position": TDWUtils.array_to_vector3(position)})
    c.communicate(commands)
c.communicate({"$type": "terminate"})
