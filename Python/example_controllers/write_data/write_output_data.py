from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.output_data_writer import OutputDataWriter
from tdw.add_ons.object_manager import ObjectManager
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Write raw output data per frame from the build.
"""

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("resp_saver")
print(f"Output data will be saved to: {path}")
c = Controller()
# Add an ObjectManager, which will start requesting output data.
object_manager = ObjectManager()
# Add an OutputDataWriter.
writer = OutputDataWriter(output_directory=path)
c.add_ons.extend([object_manager, writer])
# Get an object ID
object_id = 0
# Load the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=object_id,
                                                  position={"x": 0, "y": 5, "z": 0}))
# Frame 0: Send the commands.
c.communicate(commands)
# Print the position of the object.
print("Frame 0:", object_manager.transforms[object_id].position[1])
# Frame 1: End the simulation.
c.communicate({"$type": "terminate"})
# Print the position of the object.
print("Frame 1:", object_manager.transforms[object_id].position[1])
# Load the saved data.
print("Reading saved data...")
frame_0 = writer.read(0)
frame_1 = writer.read(1)
# Create a new ObjectManager and set `initialized` to True because we don't need to send initialization commands.
object_manager = ObjectManager()
object_manager.initialized = True
# Call `on_send(frame_0) to reproduce the data at frame 0.
object_manager.on_send(resp=frame_0)
# Print the position of the object.
print("Frame 0:", object_manager.transforms[object_id].position[1])
# Call `on_send(frame_1) to reproduce the data at frame 1.
object_manager.on_send(resp=frame_1)
# Print the position of the object.
print("Frame 1:", object_manager.transforms[object_id].position[1])
