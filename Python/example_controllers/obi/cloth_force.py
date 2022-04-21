from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.obi_data.cloth.tether_type import TetherType

"""
Apply a force to a cloth.
"""

c = Controller()
cloth_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
# Add a cloth sheet.
obi.create_cloth_sheet(cloth_material="canvas",
                       object_id=cloth_id,
                       position={"x": 1, "y": 2.0, "z": -1},
                       tether_positions={TetherParticleGroup.center: TetherType(object_id=cloth_id)})
# Apply a force to the cloth.
obi.apply_force_to_cloth(object_id=cloth_id,
                         force={"x": 0.5, "y": 0, "z": 15})
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(150):
    c.communicate([])
c.communicate({"$type": "terminate"})
