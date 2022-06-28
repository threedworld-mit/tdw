from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Minimal example of dropping a cloth sheet onto an object.
"""

c = Controller(launch_build=False)
camera = ThirdPersonCamera(position={"x": -5.0, "y": 0.8, "z": -1},
                           look_at={"x": 0, "y": 1, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
c.communicate([TDWUtils.create_empty_room(12, 12)])
c.communicate([{"$type": "create_obi_solver"}])
obi.set_solver(solver_id=0, substeps=2)
obi.set_solver(solver_id=1, substeps=2)
c.communicate([{"$type": "create_obi_solver"}])
obi.set_solver(solver_id=2, substeps=2)
# Create a softbody object, using the first solver created by the add-on.
obi.create_softbody(softbody_material="hard_rubber",
                    object_id=Controller.get_unique_id(),
                    position={"x": 0, "y": 3, "z": 2},
                    rotation={"x": -10, "y": 0, "z": 10},
                    solver_id=0)

obi.create_softbody(softbody_material="water_balloon",
                    object_id=Controller.get_unique_id(),
                    position={"x": 0, "y": 3, "z": 0},
                    rotation={"x": 10, "y": 0, "z": 10},
                    solver_id=1)
# Create a second softbody object with a different material, using the second solver.

obi.create_softbody(softbody_material="soft_foam",
                    object_id=Controller.get_unique_id(),
                    position={"x": 0, "y": 3, "z": -2},
                    rotation={"x": 15, "y": 0, "z": -15},
                    solver_id=2)

# Let the object fall.
while True:
    c.communicate([])
#c.communicate({"$type": "terminate"})
