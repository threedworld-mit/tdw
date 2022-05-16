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
obi = Obi()
c.add_ons.extend([camera, obi])
# Increase the solver substeps to accommodate the high viscosity and smoothing and make the fluid behave more like jam.
obi.set_solver(substeps=2)
# Create a softbody object.
obi.create_softbody(softbody_material="hard_rubber",
                    object_id=Controller.get_unique_id(),
                    position={"x": 0, "y": 2, "z": 0},
                    rotation={"x": 0, "y": 0, "z": 0})
commands = [TDWUtils.create_empty_room(12, 12)]
c.communicate(commands)
# Let the cloth fall.
while True:
    c.communicate([])
#c.communicate({"$type": "terminate"})
