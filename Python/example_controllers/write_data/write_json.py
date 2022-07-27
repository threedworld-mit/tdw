import json
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.json_writer import JsonWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Write TDW data class objects as JSON data and then read them.
"""

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("encode_json")
if not output_directory.exists():
    output_directory.mkdir(parents=True)
print(f"Data will be saved to: {output_directory}")
c = Controller()
# Add a robot.
robot = Robot(name="ur5")
# Add a JSON writer.
writer = JsonWriter(objects={"robot": robot}, output_directory=output_directory, include_hidden_fields=False, indent=2, zero_padding=8)
c.add_ons.extend([robot, writer])
# Create the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
# End the simulation.
c.communicate({"$type": "terminate"})
# Print the JSON dictionary.
path = output_directory.joinpath("robot_00000000.json")
text = path.read_text(encoding="utf-8")
print(json.loads(text))
