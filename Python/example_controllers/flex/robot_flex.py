from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot


c = Controller()
robot = Robot(name="ur5", robot_id=0)
c.add_ons.append(robot)
object_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="cube",
                                library="models_flex.json",
                                object_id=object_id,
                                position={"x": 0.75, "y": 0, "z": 0}),
               {"$type": "create_flex_container",
                "collision_distance": 0.075,
                "static_friction": 0.1,
                "dynamic_friction": 0.1,
                "particle_friction": 0.1,
                "iteration_count": 5,
                "substep_count": 2,
                "radius": 0.225,
                "damping": 0,
                "solid_rest": 0.15,
                "fluid_rest": 0.1425,
                "surface_tension": 0.01,
                "drag": 0},
               {"$type": "set_flex_cloth_actor",
                "id": object_id,
                "mesh_tesselation": 1,
                "stretch_stiffness": 1,
                "bend_stiffness": 1,
                "tether_stiffness": 0,
                "tether_give": 0,
                "pressure": 0.1,
                "mass_scale": 1},
               {"$type": "assign_flex_container",
                "container_id": 0,
                "id": object_id}])
robot.set_joint_targets(targets={robot.static.joint_ids_by_name["shoulder_link"]: -70})
while robot.joints_are_moving():
    c.communicate([])
