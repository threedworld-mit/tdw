from time import sleep
from tdw.add_ons.ui_widgets.loading_screen import LoadingScreen
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera


"""
Add a loading screen and then create a scene.
"""

c = Controller()
loading_screen = LoadingScreen()
camera = ThirdPersonCamera(position={"x": 0, "y": 1.8, "z": 0})

# Always add the loading screen last, so that it is destroyed at the right time.
c.add_ons.extend([camera, loading_screen])

# Create the scene.
c.communicate(Controller.get_add_scene(scene_name="mm_craftroom_1a"))

# Wait a few seconds to show that the scene has loaded and the screen has been destroyed.
sleep(5)

c.communicate({"$type": "terminate"})
