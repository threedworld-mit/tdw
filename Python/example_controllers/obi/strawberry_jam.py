from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.disk_emitter import DiskEmitter
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial
from tdw.obi_data.collision_materials.material_combine_mode import MaterialCombineMode

"""
Create a custom "strawberry jam" fluid, and a custom collision material.
Adjust solver substeps for high viscosity fluid simulation.
"""

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
fluid_id = Controller.get_unique_id()
object_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0, "z": 0})

# Define a sticky collision material.
sticky_material = CollisionMaterial(dynamic_friction=0.8,
                                    static_friction=0.8,
                                    stickiness=0.9,
                                    stick_distance=0.1,
                                    stickiness_combine=MaterialCombineMode.average,
                                    friction_combine=MaterialCombineMode.average)
# Define a custom fluid.
fluid = Fluid(capacity=1500,
              resolution=0.75,
              color={"r": 1.0, "g": 0.1, "b": 0.1, "a": 1.0},
              rest_density=1000,
              reflection=0.25,
              refraction=0.05,
              smoothing=2.5,
              viscosity=2.5,
              vorticity=0,
              surface_tension=1,
              transparency=0.85,
              radius_scale=2.0)
# Initialize Obi.
obi = Obi(floor_material=sticky_material, object_materials={object_id: sticky_material})
c.add_ons.extend([camera, obi])
# Increase the solver substeps to accommodate the high viscosity and smoothing and make the fluid behave more like jam.
obi.set_solver(substeps=4)
# Create a disk-shaped emitter, pointing straight down.
obi.create_fluid(fluid=fluid,
                 shape=DiskEmitter(radius=0.2),
                 object_id=fluid_id,
                 position={"x": -0.1, "y": 2.0, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 lifespan=20,
                 speed=2)
# Add an object for the fluid to interact with.
c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=object_id,
                                                library="models_flex.json",
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x": 0.5, "y": 0.5, "z": 0.5}))
for i in range(500):
    c.communicate([])
c.communicate({"$type": "terminate"})