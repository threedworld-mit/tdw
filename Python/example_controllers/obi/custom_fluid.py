from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.cube_emitter import CubeEmitter
from tdw.obi_data.fluids.fluid import Fluid

"""
Add a custom fluid to the scene.
"""

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
fluid_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
# Define a custom fluid.
fluid = Fluid(capacity=1000,
              resolution=0.5,
              color={"r": 0.8, "g": 0.8, "b": 0.8, "a": 1.0},
              rest_density=1000,
              reflection=0.95,
              refraction=0,
              smoothing=3.0,
              render_smoothness=1.0,
              metalness=0.1,
              viscosity=0.5,
              absorption=0,
              vorticity=0,
              surface_tension=2.0,
              transparency=0.15,
              thickness_cutoff=2,
              radius_scale=1.5,
              random_velocity=0.125)
# Create the fluid.
obi.create_fluid(fluid=fluid,
                 shape=CubeEmitter(),
                 object_id=fluid_id,
                 position={"x": -0.1, "y": 2.0, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 lifespan=6,
                 speed=0.75)
# Add an object for the fluid to interact with.
c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=Controller.get_unique_id(),
                                                library="models_flex.json",
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x": 0.5, "y": 0.5, "z": 0.5}))
for i in range(500):
    c.communicate([])
c.communicate({"$type": "terminate"})
