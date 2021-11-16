from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import OutputData, NavMeshPath
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from magnebot import Magnebot, ActionStatus

"""
Add a Magnebot to the scene and navigate using a NavMesh.
"""

c = Controller()
magnebot = Magnebot(position={"x": 0.1, "y": 0, "z": -1.3},
                    robot_id=c.get_unique_id())
magnebot.collision_detection.objects = False
camera = ThirdPersonCamera(position={"x": 0, "y": 8, "z": 0},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="c")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("nav_mesh")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["c"], path=path)
c.add_ons.extend([magnebot, camera, capture])
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      {"$type": "bake_nav_mesh"},
                      c.get_add_object(model_name="trunck",
                                       object_id=0,
                                       position={"x": 0, "y": 0, "z": 0}),
                      {"$type": "make_nav_mesh_obstacle",
                       "id": 0,
                       "carve_type": "stationary",
                       "scale": 1,
                       "shape": "box"},
                      c.get_add_object(model_name="rh10",
                                       object_id=1,
                                       position={"x": -1, "y": 0, "z": 1.5}),
                      {"$type": "make_nav_mesh_obstacle",
                       "id": 1,
                       "carve_type": "all",
                       "scale": 1,
                       "shape": "box"},
                      {"$type": "send_nav_mesh_path",
                       "origin": {"x": 0.1, "y": 0, "z": -1.3},
                       "destination": {"x": -2, "y": 0, "z": 4}}])
path = []
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "path":
        nav_mesh_path = NavMeshPath(resp[i])
        path = nav_mesh_path.get_path()
        break
for point in path[1:]:
    p = TDWUtils.array_to_vector3(point)
    p["y"] = 0
    magnebot.move_to(target=p)
    while magnebot.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])
c.communicate({"$type": "terminate"})