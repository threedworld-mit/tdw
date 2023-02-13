from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Capture image data from the Replicant per `communicate()` call and save it to disk.
"""

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_egocentric")
print(f"Images will be saved to: {path}")
c = Controller()
# Request image data on every `communicate()` call.
replicant = Replicant(image_frequency=ImageFrequency.always)
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
replicant.move_by(2)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
    # Save the images.
    replicant.dynamic.save_images(output_directory=path)
c.communicate([])
# Save the images.
replicant.dynamic.save_images(output_directory=path)
c.communicate({"$type": "terminate"})
