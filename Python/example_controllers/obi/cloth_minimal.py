from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Minimal example of dropping a cloth sheet onto an object.
"""

c = Controller(launch_build=False)
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi(output_data=False)
c.add_ons.extend([camera, obi])
obi.create_cloth_sheet(cloth_material="cotton",
                       object_id=Controller.get_unique_id(),
                       position={"x": 0, "y": 2.0, "z": 0},
                       rotation={"x": 0, "y": 0, "z": 0})
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=Controller.get_unique_id()))
c.communicate(commands)
# Let the cloth object settle.
for i in range(150):
    c.communicate([])

c.communicate({"$type": "terminate"})
