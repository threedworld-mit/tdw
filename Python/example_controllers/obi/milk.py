from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.disk_emitter import DiskEmitter
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial
from tdw.obi_data.collision_materials.material_combine_mode import MaterialCombineMode


"""
Create a custom collision material to simulate a slick fluid.
"""

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
fluid_id = Controller.get_unique_id()
object_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0, "z": 0})
# Define a slick collision material.
slick_material = CollisionMaterial(dynamic_friction=0.05,
                                   static_friction=0.05,
                                   stickiness=0,
                                   stick_distance=0,
                                   stickiness_combine=MaterialCombineMode.average,
                                   friction_combine=MaterialCombineMode.average)
obi = Obi(floor_material=slick_material, object_materials={object_id: slick_material})
c.add_ons.extend([camera, obi])
obi.create_fluid(fluid="milk",
                 shape=DiskEmitter(radius=0.25),
                 object_id=fluid_id,
                 position={"x": -0.1, "y": 2.0, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 lifespan=12,
                 speed=3)
# Add an object for the fluid to interact with.
c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=object_id,
                                                library="models_flex.json",
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x": 0.5, "y": 0.5, "z": 0.5}))
for i in range(300):
    c.communicate([])
c.communicate({"$type": "terminate"})
