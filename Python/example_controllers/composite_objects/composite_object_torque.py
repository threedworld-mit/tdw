from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Apply a torque to the door of a microwave.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": 1, "y": 1.5, "z": 0.3},
                           look_at={"x": 0, "y": 0, "z": 0})
composite_object_manager = CompositeObjectManager()
c.add_ons.extend([camera, composite_object_manager])
# Create the scene and add the object.
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                                  object_id=object_id,
                                                  kinematic=True))
c.communicate(commands)
# Get the hinge ID.
hinge_id = list(composite_object_manager.static[object_id].hinges.keys())[0]
# Apply a torque to the hinge.
c.communicate({"$type": "apply_torque_to_object",
               "id": hinge_id,
               "torque": {"x": 0.5, "y": 0, "z": 0}})
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
