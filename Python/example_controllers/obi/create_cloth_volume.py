from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial
from tdw.obi_data.collision_materials.material_combine_mode import MaterialCombineMode



"""
Minimal example of adding a cloth sheet to a scene.
"""

c = Controller(launch_build=False)
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
cloth_id = Controller.get_unique_id()
receptacle_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0.5, "z": 0})
# Define a  collision material.
coll_material = CollisionMaterial(dynamic_friction=0.5,
                                       static_friction=0.5,
                                       stickiness=0.5,
                                       stick_distance=0.1,
                                       stickiness_combine=MaterialCombineMode.average,
                                       friction_combine=MaterialCombineMode.average)

obi = Obi(output_data=False, floor_material=coll_material, object_materials={cloth_id: coll_material})
c.add_ons.extend([camera, obi])

# Create a disk-shaped emitter, pointing straight down.
obi.create_cloth_volume(cloth_material="silk",
                        object_id=cloth_id,
                        position={"x": 0, "y": 2.0, "z": 0},
                        rotation={"x": 0, "y": 0, "z": 0},
                        volume_type="ball",
                        pressure=3.0,
                        solver_id=0)
c.communicate([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5}])
c.communicate({"$type": "set_obi_solver_substeps",  "solver_id": 0, "substeps": 2});

for i in range(600):
    c.communicate([])
c.communicate({"$type": "terminate"})