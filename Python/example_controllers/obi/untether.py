from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.sheet_type import SheetType
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.obi_data.cloth.tether_type import TetherType

"""
Tether and then un-tether a cloth sheet.
"""

c = Controller()
cloth_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
# Create the cloth sheet and tether it.
obi.create_cloth_sheet(cloth_material="canvas",
                       object_id=cloth_id,
                       position={"x": 0, "y": 3.0, "z": 0},
                       sheet_type=SheetType.cloth_hd,
                       tether_positions={TetherParticleGroup.center: TetherType(cloth_id)})
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(100):
    c.communicate([])
# Un-tether the cloth sheet.
obi.untether_cloth_sheet(object_id=cloth_id, tether_position=TetherParticleGroup.center)
for i in range(100):
    c.communicate([])
c.communicate({"$type": "terminate"})
