from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.robot import Robot
from tdw.obi_data.fluids.cube_emitter import CubeEmitter

"""
Add a robot and an Obi fluid to the scene.
"""

c = Controller()
# Add Obi.
obi = Obi()
# Add a robot.
robot = Robot(name="fetch", position={"x": -0.5, "y": 0, "z": 0})
# Add a camera.
camera = ThirdPersonCamera(position={"x": 2.7, "y": 2.5, "z": -1.75},
                           look_at={"x": 0, "y": 0, "z": 0})
c.add_ons.extend([obi, robot, camera])
# Create the scene, including an object.
commands = [Controller.get_add_scene(scene_name="tdw_room")]
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.5, "y": 0, "z": 0}))
c.communicate(commands)
# Create a fluid.
obi.create_fluid(fluid="water",
                 object_id=Controller.get_unique_id(),
                 position={"x": 0, "y": 0.5, "z": 1},
                 rotation={"x": 0, "y": 180, "z": 0},
                 speed=3,
                 shape=CubeEmitter(size={"x": 0.5, "y": 0.5, "z": 0.5}))
for i in range(100):
    c.communicate([])
c.communicate({"$type": "terminate"})
