from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.cloth_material import ClothMaterial
from tdw.obi_data.cloth.sheet_type import SheetType

"""
Add a cloth sheet with a custom material to the scene.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
# Define a custom cloth material.
cloth_material = ClothMaterial(visual_material="3d_printed_mesh_round",
                               texture_scale={"x": 2, "y": 2},
                               stretching_scale=1,
                               stretch_compliance=0,
                               max_compression=0,
                               max_bending=0.1,
                               drag=0.17,
                               lift=0.17,
                               visual_smoothness=0.9,
                               mass_per_square_meter=0.1)
obi.create_cloth_sheet(cloth_material=cloth_material,
                       object_id=Controller.get_unique_id(),
                       position={"x": 0, "y": 3.5, "z": 0},
                       rotation={"x": 0, "y": 0, "z": 0},
                       sheet_type=SheetType.cloth_hd)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                  object_id=Controller.get_unique_id(),
                                                  library="models_flex.json",
                                                  kinematic=True,
                                                  gravity=False,
                                                  scale_factor={"x": 0.5, "y": 0.5, "z": 0.5}))
c.communicate(commands)
# Let the cloth fall.
for i in range(350):
    c.communicate([])
c.communicate({"$type": "terminate"})
