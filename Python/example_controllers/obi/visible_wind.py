from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.wind_source import WindSource
from tdw.tdw_utils import TDWUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
Add a wind source and make it visible.
"""

c = Controller()
wind_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": 1.1, "y": 1.32, "z": -1.9},
                           look_at={"x": -2, "y": 0, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("visible_wind")
print(f"Image will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
obi = Obi()
c.add_ons.extend([camera, capture, obi])
# Add a wind source. Make it visible.
wind_source = WindSource(wind_id=wind_id,
                         position={"x": -0.1, "y": 0, "z": 0.25},
                         rotation={"x": 0, "y": -90, "z": 0},
                         emitter_radius=1,
                         capacity=5000,
                         speed=30,
                         lifespan=2,
                         smoothing=0.75,
                         visible=True)
obi.wind_sources[wind_id] = wind_source
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
