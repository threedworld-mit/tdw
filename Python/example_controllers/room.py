from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller(launch_build=False)
cam = ThirdPersonCamera(position={"x": 0, "y": 1, "z": 0},
                        look_at={"x": 4.5, "y": 0, "z": 4.5})
c.add_ons.append(cam)
c.communicate({"$type": "add_scene",
               "name": "reference_task_room",
               "url": "https://tdw-public.s3.amazonaws.com/scenes/webgl/2020.3/reference_task_room"})