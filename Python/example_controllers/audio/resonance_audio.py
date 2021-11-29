from typing import Dict
from time import sleep
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer


class Audio(Controller):
    """
    Create a scene with a reverb space and audio sensor. Test how object positions can affect reverb.
    """

    def delay_and_teleport(self, id_0: int, id_1: int, pos_0: Dict[str, float], pos_1: Dict[str, float]) -> None:
        """
        Wait ten seconds and then teleport the objects.

        :param id_0: The ID of the first object.
        :param id_1: The ID of the second object.
        :param pos_0: The new position of the first object.
        :param pos_1: The new position of the second object.
        """

        sleep(10)
        self.communicate([{"$type": "teleport_object",
                           "id": id_0,
                           "position": pos_0},
                          {"$type": "teleport_object",
                           "id": id_1,
                           "position": pos_1}])

    def run(self) -> None:
        pos_0 = {"x": 3.16, "y": 0, "z": 4.34}
        pos_1 = {"x": -2.13, "y": 0, "z": -1.0}
        pos_2 = {"x": -1.9, "y": 0, "z": 1.45}
        pos_3 = {"x": 2.4, "y": 0, "z": -4.3}
        pos_4 = {"x": 0, "y": 0, "z": 0}

        object_id_0 = self.get_unique_id()
        object_id_1 = self.get_unique_id()
        audio_id_0 = self.get_unique_id()
        audio_id_1 = self.get_unique_id()

        # Add a camera.
        camera = ThirdPersonCamera(position={"x": -4, "y": 1.5, "z": 0},
                                   look_at={"x": 2.5, "y": 0, "z": 0},
                                   avatar_id="a",
                                   field_of_view=75)
        # Enable Resonance Audio.
        audio = ResonanceAudioInitializer(avatar_id="a",
                                          floor="marble")
        self.add_ons.extend([camera, audio])

        # Load the scene.
        # Add two objects. Make both objects kinematic.
        self.communicate([self.get_add_scene(scene_name="tdw_room"),
                          self.get_add_object(model_name="satiro_sculpture",
                                              position=pos_0,
                                              rotation={"x": 0.0, "y": -108, "z": 0.0},
                                              library="models_core.json",
                                              object_id=object_id_0),
                          self.get_add_object(model_name="buddah",
                                              position=pos_1,
                                              rotation={"x": 0.0, "y": 90, "z": 0.0},
                                              library="models_core.json",
                                              object_id=object_id_1),
                          {"$type": "set_kinematic_state",
                           "id": object_id_0,
                           "is_kinematic": True,
                           "use_gravity": False},
                          {"$type": "set_kinematic_state",
                           "id": object_id_1,
                           "is_kinematic": True,
                           "use_gravity": False}])
        # Start to play audio on both objects.
        # Parent each audio source to its corresponding object.
        audio.play(path="HWL_1b.wav",
                   audio_id=audio_id_0,
                   object_id=object_id_0,
                   position={"x": pos_0["x"], "y": pos_0["y"] + 0.85, "z": pos_0["z"]})
        audio.play(path="HWL_3c.wav",
                   audio_id=audio_id_1,
                   object_id=object_id_1,
                   position={"x": pos_1["x"], "y": pos_1["y"] + 0.85, "z": pos_1["z"]})
        self.communicate([])

        # Every ten seconds, adjust the positions of the objects.
        self.delay_and_teleport(object_id_0, object_id_1, pos_1, pos_0)
        self.delay_and_teleport(object_id_0, object_id_1, pos_2, pos_3)
        self.delay_and_teleport(object_id_0, object_id_1, pos_3, pos_2)
        self.delay_and_teleport(object_id_0, object_id_1, pos_2, pos_4)
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    Audio().run()
