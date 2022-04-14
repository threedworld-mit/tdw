from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.obi_data.cloth.tether_position import TetherPosition
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH



"""
Minimal example of dropping a cloth sheet onto an object.
"""

c = Controller(launch_build=False)
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi(output_data=False)
c.add_ons.extend([camera, obi])
cloth_id = Controller.get_unique_id()
cube_id = Controller.get_unique_id()
# Create a sheet that looks and behaves like canvas, that we will attach to a bar-shaped object.
# Note the offset in Z, required to line up the "north" edge of the sheet with the object.
obi.create_cloth_sheet(cloth_material="cotton",
                       object_id=cloth_id,
                       position={"x": 0, "y": 4.0, "z": -3.0},
                       rotation={"x": 0, "y": 0, "z": 0},
                       tether_positions=[TetherPosition(other_id=cube_id,
                                                        particle_group=TetherParticleGroup.north_edge)])
# Create the long bar-shaped attachment object.
c.communicate(Controller.get_add_physics_object(model_name="cube",
                                                object_id=cube_id,
                                                library="models_flex.json",
                                                position={"x": 0, "y": 2.0, "z": 0},
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x": 3.0, "y": 0.1, "z": 0.1}))
c.communicate([{"$type": "set_obi_solver_substeps",  "solver_id": 0, "substeps": 2},
               {"$type": "set_obi_solver_scale",  "solver_id": 0, "scale_factor": 0.5}])

# Let the cloth object settle.
for i in range(150):
    c.communicate([])

# Rotate the bar back and forth, moving the cloth with it.
for i in range(480):
    c.communicate({"$type": "rotate_object_by", "id": cube_id, "axis": "yaw", "is_world": False, "angle": 1})
   
for i in range(540):
    c.communicate({"$type": "rotate_object_by", "id": cube_id, "axis": "yaw", "is_world": False,  "angle": -1})

c.communicate({"$type": "terminate"})
