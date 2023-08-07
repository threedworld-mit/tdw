from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.wind_source import WindSource
from tdw.obi_data.cloth.sheet_type import SheetType
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.obi_data.cloth.tether_type import TetherType
from tdw.tdw_utils import TDWUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Control a wind source's gustiness.
"""

c = Controller()
wind_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": 1.1, "y": 1.32, "z": -1.9},
                           look_at={"x": -2, "y": 0, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("gust")
print(f"Image will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
obi = Obi()
c.add_ons.extend([camera, capture, obi])
# Add a wind source.
wind_source = WindSource(wind_id=wind_id,
                         position={"x": -0.1, "y": 0, "z": 0.25},
                         rotation={"x": 0, "y": -90, "z": 0},
                         capacity=15000,
                         lifespan=1,
                         speed=15,
                         emitter_radius=0.5,
                         smoothing=0.75,
                         visible=True)
obi.wind_sources[wind_id] = wind_source
cloth_id = Controller.get_unique_id()
obi.create_cloth_sheet(cloth_material="canvas",
                       object_id=cloth_id,
                       position={"x": -3, "y": 1.6, "z": 0.2},
                       rotation={"x": -90, "y": 90, "z": 0},
                       sheet_type=SheetType.cloth,
                       tether_positions={TetherParticleGroup.north_edge: TetherType(object_id=cloth_id, is_static=True)})

c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(300):
    c.communicate([])
# Switch to wind gusts.
obi.wind_sources[wind_id].set_gustiness(capacity=9000, dc=100, lifespan=2, dl=0.1)
gusting = True
while gusting:
    c.communicate([])
    dc, dl = obi.wind_sources[wind_id].is_gusting()
    gusting = dc and dl
# Wind gusts.
for i in range(400):
    c.communicate([])
c.communicate({"$type": "terminate"})
