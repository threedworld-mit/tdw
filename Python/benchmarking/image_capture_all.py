from math import sin, cos, pi
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.benchmark import Benchmark

c = Controller()
benchmark = Benchmark()
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": 1, "z": 0})
c.add_ons.extend([camera, benchmark])
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
commands = [{"$type": "set_pass_masks",
             "pass_masks": ["_img", "_id", "_mask", "_category", "_depth", "_normals", "_flow", "_depth_simple", "_albedo"]},
            {"$type": "send_images",
             "frequency": "always"}]
n = 15
da = (2 * pi) / n
angle = 0
r = 1.75
for i in range(n):
    x = cos(angle) * r
    z = sin(angle) * r
    commands.append(Controller.get_add_object(model_name="chair_billiani_doll",
                                              object_id=Controller.get_unique_id(),
                                              position={"x": x, "y": 0, "z": z}))
    angle += da
c.communicate(commands)
benchmark.start()
for i in range(360):
    camera.rotate({"x": 0, "y": 1, "z": 0})
    c.communicate([])
benchmark.stop()
c.communicate({"$type": "terminate"})
print(benchmark.fps, sum(benchmark.times))
