from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Generate object output data per-frame until all objects stop moving.
Save the data to disk as a numpy array.
"""

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("object_output_data/output.npy")
if not path.parent.exists():
    path.parent.mkdir(parents=True)

c = Controller()
print(f"Output will be saved to: {path.resolve()}")
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 6, "z": 0},
                             rotation={"x": 25, "y": 38, "z": -10},
                             object_id=object_id),
            {"$type": "send_transforms",
             "frequency": "always",
             "ids": [object_id]},
            {"$type": "send_rigidbodies",
             "frequency": "always",
             "ids": [object_id]}]

# Send the commands.
resp = c.communicate(commands)

# The position of the object per frame.
positions: List[np.array] = list()
# If True, the object has stopped moving.
sleeping = False

# Wait for the object to stop moving.
while not sleeping:
    for i in range(len(resp) - 1):
        # Get the output data ID.
        r_id = OutputData.get_data_type_id(resp[i])
        # This is transforms output data.
        if r_id == "tran":
            transforms = Transforms(resp[i])
            for j in range(transforms.get_num()):
                if transforms.get_id(j) == object_id:
                    # Log the position.
                    positions.append(transforms.get_position(j))
        elif r_id == "rigi":
            rigidbodies = Rigidbodies(resp[i])
            for j in range(rigidbodies.get_num()):
                if rigidbodies.get_id(j) == object_id:
                    # Check if the object is sleeping.
                    sleeping = rigidbodies.get_sleeping(j)
    # Advance another frame and continue the loop.
    if not sleeping:
        resp = c.communicate([])
# Save the numpy array (remove the file extension).
np.save(str(path.resolve())[:-4], np.array(positions))
c.communicate({"$type": "terminate"})
