from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.json_writer import JsonWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
An example of multi-agent JSON serialization.
"""

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_agent_json")
c = Controller()
# Add two agents.
robot_0 = Robot(name="ur5",
                robot_id=0,
                position={"x": 3, "y": 0, "z": 1})
robot_1 = Robot(name="ur5", robot_id=1)
# Add a JSON writer. Write data for both agents.
writer = JsonWriter(objects={"robot_0": robot_0,
                             "robot_1": robot_1},
                    output_directory=output_directory)
c.add_ons.extend([robot_0, robot_1, writer])
# Load an empty scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
c.communicate({"$type": "terminate"})
print(writer.read(0))
