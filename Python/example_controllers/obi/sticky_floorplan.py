from tdw.controller import Controller
from tdw.add_ons.floorplan import Floorplan
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.obi import Obi
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial
from tdw.obi_data.collision_materials.material_combine_mode import MaterialCombineMode


"""
Make a floorplan scene very sticky.
"""

c = Controller()
floorplan = Floorplan()
object_manager = ObjectManager()
obi = Obi()
c.add_ons.extend([floorplan, object_manager, obi])

# Initialize the scene.
floorplan.init_scene(scene="1a", layout=0)
c.communicate([])

# Define a sticky collision material.
collision_material = CollisionMaterial(dynamic_friction=0.3,
                                       static_friction=0.3,
                                       stickiness=1,
                                       stick_distance=0.1,
                                       stickiness_combine=MaterialCombineMode.average,
                                       friction_combine=MaterialCombineMode.average)
# Get a dictionary of object IDs and collision material.
object_materials = {object_id: collision_material for object_id in object_manager.objects_static}
# Reset Obi and apply the collision material.
obi.reset(floor_material=collision_material,
          object_materials=object_materials)
# Call `communicate()` to update the scene.
c.communicate([])
# End the simulation.
c.communicate({"$type": "terminate"})
