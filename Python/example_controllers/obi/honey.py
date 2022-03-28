from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.fluids.cube_emitter import CubeEmitter


"""
Minimal example of adding honey to a scene.
"""

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
fluid_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": 1.2, "y": 1.5, "z": -1.5},
                           look_at={"x": 0, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.create_fluid(fluid="honey",
                 shape=CubeEmitter(),
                 object_id=fluid_id,
                 position={"x": 0, "y": 2.35, "z": 0},
                 rotation={"x": 90, "y": 0, "z": 0},
                 speed=1)
c.communicate(Controller.get_add_physics_object(model_name="rh10",
                                                object_id=Controller.get_unique_id()))
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
