import wave
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
import base64
from time import sleep


"""
- Create a scene with a reverb space and audio sensor.
- Test how object positions can affect reverb.
"""


class Audio(Controller):
    def play_point_sound(self, bytes, id, offset=0.85):
        """
        Example of how to send raw audio data over the socket
        and have it played by an object as a Resonance Audio localized point source.
        """

        data = str(base64.b64encode(bytes), 'ascii', 'ignore')
        self.communicate({"$type": "play_point_source_data",
                          "id": id,
                          "num_frames": len(bytes),
                          "num_channels": 1,
                          "frame_rate": 44100,
                          "wav_data": data,
                          "y_pos_offset": offset})

    def delay_and_teleport(self, id_0, id_1, pos_0, pos_1):
        # Wait 10 seconds.
        sleep(10)

        # Swap positions.
        self.communicate([{"$type": "teleport_object",
                           "id": id_0,
                           "position": pos_0},
                          {"$type": "teleport_object",
                           "id": id_1,
                           "position": pos_1}
                          ])

    @staticmethod
    def open_wav(filename):
        """
        Open a .wav file. Returns the parameters and bytes of the file.

        :param filename: The filename.
        """
        w = wave.open(filename, 'rb')
        return w.readframes(w.getparams().nframes)

    def run(self):
        pos_0 = {"x": 3.16, "y": 0, "z": 4.34}
        pos_1 = {"x": -2.13, "y": 0, "z": -1.0}
        pos_2 = {"x": -1.9, "y": 0, "z": 1.45}
        pos_3 = {"x": 2.4, "y": 0, "z": -4.3}
        pos_4 = {"x": 0, "y": 0, "z": 0}

        # Load the streamed scene.
        self.load_streamed_scene(scene="tdw_room_2018")
        # Create the objects.
        id_0 = self.add_object("satiro_sculpture",
                               position=pos_0,
                               rotation={"x": 0.0, "y": -108.0, "z": 0.0},
                               library="models_core.json")
        id_1 = self.add_object("buddah",
                               position=pos_1,
                               rotation={"x": 0.0, "y": 90, "z": 0.0},
                               library="models_core.json")

        # Set both objects to kinematic.
        self.communicate([{"$type": "set_kinematic_state",
                           "id": id_0,
                           "is_kinematic": True,
                           "use_gravity": False},
                          {"$type": "set_kinematic_state",
                           "id": id_1,
                           "is_kinematic": True,
                           "use_gravity": False}
                          ])

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(
            position={"x": -4, "y": 1.5, "z": 0},
            look_at={"x": 2.5, "y": 0, "z": 0}))
        # Add the audio sensor.
        # Set the field of view.
        self.communicate([{"$type": "add_environ_audio_sensor",
                           "avatar_id": "a"},
                          {"$type": "set_field_of_view",
                           "avatar_id": "a",
                           "field_of_view": 75.0}
                          ])
        # Create the reverb space.
        self.communicate({"$type": "set_reverb_space_simple",
                          "env": 0,
                          "reverb_floor_material": "marble"})

        # Start playing each sound.
        self.play_point_sound(Audio.open_wav("HWL_1b.wav"), id_0)
        self.play_point_sound(Audio.open_wav("HWL_3c.wav"), id_1)

        self.delay_and_teleport(id_0, id_1, pos_1, pos_0)
        self.delay_and_teleport(id_0, id_1, pos_2, pos_3)
        self.delay_and_teleport(id_0, id_1, pos_3, pos_2)
        self.delay_and_teleport(id_0, id_1, pos_2, pos_4)


if __name__ == "__main__":
    Audio().run()
