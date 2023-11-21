import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.output_data_writer import OutputDataWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Write raw output data per frame from the build into a .zip file.
"""

c = Controller(launch_build=False)
# Add a camera.
camera = ThirdPersonCamera(position={"x": 0.5, "y": 1.9, "z": -4},
                           avatar_id="a",
                           look_at=TDWUtils.VECTOR3_ZERO)
c.add_ons.append(camera)
# Write output data to a zip file.
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("output_data_writer")
print(f"Output will be saved to: {output_directory}")
writer = OutputDataWriter(output_directory=output_directory, zip_filename="output.zip")
c.add_ons.append(writer)

# The vases will be these colors.
colors = [{"r": 1, "g": 0, "b": 0, "a": 1},
          {"r": 0, "g": 1, "b": 0, "a": 1},
          {"r": 0, "g": 0, "b": 1, "a": 1},
          {"r": 1, "g": 1, "b": 0, "a": 1},
          {"r": 1, "g": 0, "b": 1, "a": 1},
          {"r": 0, "g": 1, "b": 1, "a": 1},
          {"r": 1, "g": 1, "b": 1, "a": 1}]
color_index: int = 0

# Create a scene.
commands = [TDWUtils.create_empty_room(12, 12)]
# Define a circle of positions.
num_x = 12
num_z = 12
ir = 4
xs, zs = np.ogrid[:num_x, :num_z]
dist_from_center = np.sqrt((xs - num_x // 2) ** 2 + (zs - num_z // 2) ** 2)
mask = dist_from_center <= ir
radius = 1.75
xs = np.linspace(-radius, radius, num_x)
zs = np.linspace(-radius, radius, num_z)
object_id = 0
# Add objects in the circle.
for ix in range(num_x):
    for iz in range(num_z):
        if mask[ix][iz]:
            # Add an object.
            commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                              object_id=object_id,
                                                              library="models_core.json",
                                                              position={"x": float(xs[ix]), "y": 0, "z": float(zs[iz])}))
            # Set its color.
            commands.append({"$type": "set_color",
                             "id": object_id,
                             "color": colors[color_index]})
            # Increment the indices.
            object_id += 1
            color_index += 1
            if color_index >= len(colors):
                color_index = 0
# Add a ball.
s = 0.35
commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                  object_id=object_id,
                                                  library="models_flex.json",
                                                  position={"x": s / 2, "y": 0, "z": -radius * 2},
                                                  scale_factor={"x": s, "y": s, "z": s},
                                                  scale_mass=False,
                                                  default_physics_values=False,
                                                  mass=15,
                                                  dynamic_friction=0.1,
                                                  static_friction=0.1,
                                                  bounciness=0.9))
# Set the ball's color.
# Apply a torque and force to the ball.
commands.extend([{"$type": "set_color",
                  "id": object_id,
                  "color": colors[color_index]},
                 {"$type": "apply_force_to_object",
                  "id": object_id,
                  "force": {"x": 0, "y": 0, "z": 90}},
                 {"$type": "apply_torque_to_object",
                  "id": object_id,
                  "torque": {"x": 20, "y": 0, "z": 0}}])
# Request output data.
# On the first frame only, we need the avatar's position, the camera rotation, model names (SegmentationColors) and colors (AlbedoColors).
# This is because we know these properties won't change in this simulation.
# Per-frame, we need transforms of all objects.
commands.extend([{"$type": "send_segmentation_colors",
                  "frequency": "once"},
                 {"$type": "send_albedo_colors",
                  "frequency": "once"},
                 {"$type": "send_avatars",
                  "frequency": "once"},
                 {"$type": "send_image_sensors",
                  "frequency": "once"},
                 {"$type": "send_transforms",
                  "frequency": "always"}])
# Send the initialization commands.
c.communicate(commands)
# Run the simulation
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})