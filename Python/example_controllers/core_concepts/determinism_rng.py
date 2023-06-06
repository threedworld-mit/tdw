import numpy as np
from tdw.controller import Controller
from tdw.add_ons.robot import Robot
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.logger import Logger
from tdw.tdw_utils import TDWUtils

"""
This test verifies that, given a random seed and a controller, the build will always generate the same joint IDs, sub-object IDs, and segmentation colors. 

See also: `determinism_log.py`
"""

joint_ids = {0: np.array([147, 157, 175]),
             1008269081: np.array([195, 94, 113]),
             2005789796: np.array([0, 154, 146]),
             1706746116: np.array([138, 76, 169]),
             1922776196: np.array([207, 131, 96]),
             216757113: np.array([177, 130, 222]),
             1704308182: np.array([185, 30, 134])}
object_ids = {1: np.array([199, 145, 100]),
              1755192844: np.array([216, 138, 133])}
c = Controller()
robot = Robot(name="ur5")
object_manager = ObjectManager()
logger = Logger(path="determinism_log.txt")
c.add_ons.extend([logger, robot, object_manager])
c.communicate([{"$type": "set_random",
                "seed": 0},
               TDWUtils.create_empty_room(6, 6),
               Controller.get_add_object(model_name="microwave_composite",
                                         object_id=1,
                                         position={"x": 2, "y": 0, "z": 0})])

for object_id in object_manager.objects_static:
    assert object_id in object_ids, f"Object ID not found: {object_id}"
    color = object_manager.objects_static[object_id].segmentation_color
    assert (color == object_ids[object_id]).all(), f"Bad segmentation color for object {object_id}: {color}"

for joint_id in robot.static.joints:
    joint = robot.static.joints[joint_id]
    assert joint_id in joint_ids, f"Joint ID not found: {joint_id}"
    color = joint.segmentation_color
    assert (color == joint_ids[joint_id]).all(), f"Bad segmentation color for joint {joint_id}: {color}"

c.communicate({"$type": "terminate"})
