from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera



"""
Minimal example of adding honey to a scene.
"""

c = Controller(launch_build=False)
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
cloth_id = Controller.get_unique_id()
receptacle_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])

# Create a disk-shaped emitter, pointing straight down.
obi.create_cloth_sheet(cloth_material="cotton",
                       object_id=cloth_id,
                       position={"x": 0, "y": 2.0, "z": 0},
                       rotation={"x": 0, "y": 0, "z": 0},
                       sheet_type="cloth",
                       solver_id=0)
# Add an object for the fluid to interact with.
c.communicate(Controller.get_add_physics_object(model_name="sphere",
                                                object_id=receptacle_id,
                                                library="models_flex.json",
                                                scale_factor={"x":0.5, "y": 0.5, "z":0.5}))
for i in range(500):
    c.communicate([])
c.communicate({"$type": "terminate"})