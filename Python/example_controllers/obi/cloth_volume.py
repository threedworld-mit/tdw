from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial
from tdw.obi_data.collision_materials.material_combine_mode import MaterialCombineMode
from tdw.obi_data.cloth.volume_type import ClothVolumeType

"""
Minimal example of adding a cloth volume to a scene.
"""

c = Controller()
cloth_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0.5, "z": 0})
# Define a  collision material.
collision_material = CollisionMaterial(dynamic_friction=0.8,
                                       static_friction=0.8,
                                       stickiness=0.8,
                                       stick_distance=0.1,
                                       stickiness_combine=MaterialCombineMode.average,
                                       friction_combine=MaterialCombineMode.average)
obi = Obi(floor_material=collision_material, object_materials={cloth_id: collision_material})
c.add_ons.extend([camera, obi])
obi.set_solver(solver_id=0,
               substeps=2,
               scale_factor=0.5)
# Add the cloth volume.
obi.create_cloth_volume(cloth_material="canvas",
                        object_id=cloth_id,
                        position={"x": 0, "y": 1.0, "z": 0},
                        rotation={"x": 0, "y": 0, "z": 0},
                        volume_type=ClothVolumeType.sphere,
                        pressure=3.0,
                        solver_id=0)
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
