from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.sheet_type import SheetType
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.obi_data.cloth.tether_type import TetherType

"""
Apply multiple tether positions to a single cloth sheet.
"""

c = Controller()
cloth_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.create_cloth_sheet(cloth_material="plastic",
                       object_id=cloth_id,
                       position={"x": 1, "y": 1.0, "z": -1},
                       rotation={"x": 20, "y": 10, "z": 10},
                       sheet_type=SheetType.cloth_hd,
                       tether_positions={TetherParticleGroup.north_edge: TetherType(object_id=cloth_id, is_static=True),
                                         TetherParticleGroup.east_edge: TetherType(object_id=cloth_id)})
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(150):
    c.communicate([])
c.communicate({"$type": "terminate"})
