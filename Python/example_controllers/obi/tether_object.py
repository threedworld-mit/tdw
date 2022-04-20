from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.obi_data.cloth.tether_type import TetherType
from tdw.obi_data.cloth.sheet_type import SheetType

"""
Tether a cloth sheet to another object and scale the sheet via the solver.
"""

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
cloth_id = Controller.get_unique_id()
cube_id = Controller.get_unique_id()
# Scale the solver.
obi.set_solver(scale_factor=0.75,
               substeps=2)
# Create a sheet that looks and behaves like canvas, that we will attach to a bar-shaped object.
# Note the offset in Z, required to line up the "north" edge of the sheet with the object.
obi.create_cloth_sheet(cloth_material="canvas",
                       object_id=cloth_id,
                       position={"x": 0, "y": 2.0, "z": -1.0},
                       rotation={"x": 0, "y": 0, "z": 0},
                       sheet_type=SheetType.cloth_hd,
                       tether_positions={TetherParticleGroup.north_edge: TetherType(cube_id)})
# Create the long bar-shaped attachment object.
c.communicate(Controller.get_add_physics_object(model_name="cube",
                                                object_id=cube_id,
                                                library="models_flex.json",
                                                position={"x": 0, "y": 2.0, "z": 0},
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x": 3.0, "y": 0.1, "z": 0.1}))
# Let the cloth object settle.
for i in range(150):
    c.communicate([])
# Rotate the bar back and forth, moving the cloth with it.
for i in range(480):
    c.communicate({"$type": "rotate_object_by",
                   "id": cube_id,
                   "axis": "yaw",
                   "is_world": False,
                   "angle": 1})
for i in range(540):
    c.communicate({"$type": "rotate_object_by",
                   "id": cube_id,
                   "axis": "yaw",
                   "is_world": False,
                   "angle": -1})
c.communicate({"$type": "terminate"})
