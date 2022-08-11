from time import sleep
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer

"""
Initialize and play audio.
"""

c = Controller()
object_id_0 = c.get_unique_id()
object_id_1 = c.get_unique_id()
object_position_0 = {"x": 3.16, "y": 0, "z": 4.34}
object_position_1 = {"x": -2.13, "y": 0, "z": -1.0}
# Add a camera.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": -4, "y": 1.5, "z": 0},
                           look_at={"x": 2.5, "y": 0, "z": 0})
# Initialize audio.
audio_initializer = AudioInitializer(avatar_id="a")
c.add_ons.extend([camera, audio_initializer])
# Create the scene.
c.communicate([c.get_add_scene("tdw_room"),
               c.get_add_object(model_name="satiro_sculpture",
                                object_id=object_id_0,
                                position=object_position_0,
                                rotation={"x": 0.0, "y": -108.0, "z": 0.0}),
               c.get_add_object(model_name="buddah",
                                object_id=object_id_1,
                                position={"x": -2.13, "y": 0, "z": -1.0},
                                rotation={"x": 0.0, "y": 90, "z": 0.0})])
# Start playing audio on both objects once they are created.
audio_initializer.play(path="HWL_1b.wav", position=object_position_0)
c.communicate({"$type": "set_field_of_view",
               "avatar_id": "a",
               "field_of_view": 75.0})
sleep(10)
c.communicate({"$type": "terminate"})
