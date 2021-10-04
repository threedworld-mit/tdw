from pathlib import Path
from typing import Union
import numpy as np
from tdw.controller import Controller
from tdw.py_impact import PyImpact, AudioMaterial
from tdw.tdw_utils import TDWUtils, AudioUtils
from tdw.object_init_data import AudioInitData
from tdw.output_data import OutputData, Rigidbodies, AudioSources


class MinimalAudioDataset(Controller):
    """
    A minimal example of how to generate audio datasets.
    """

    # The PyImpact object.
    PY_IMPACT = PyImpact()
    # Audio materials for the floor and wall.
    FLOOR: AudioMaterial = AudioMaterial.wood_medium
    WALL: AudioMaterial = AudioMaterial.wood_medium

    def __init__(self, output_directory: Union[str, Path], port: int = 1071):
        super().__init__(port=port, launch_build=False)
        if isinstance(output_directory, str):
            self.output_directory: Path = Path(output_directory)
        else:
            self.output_directory: Path = output_directory
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)
        # The trial number.
        self.trial_num: int = 0
        self.communicate({"$type": "set_target_framerate",
                          "framerate": 60})

    def run(self) -> None:
        """
        Run a series of trials. Each trial generates a .wav file.
        """

        for name in ["elephant_bowl", "rh10", "pepper"]:
            self.trial(name=name)
        self.communicate({"$type": "terminate"})

    def trial(self, name: str) -> None:
        """
        In a trial, create a scene. Add an avatar with an audio sensor.
        Add an object and then drop the object.
        As the object bounces on the floor, generate audio.
        Record the audio and save it to disk as a .wav file.

        :param name: The name of the model.
        """

        # Reset PyImpact.
        MinimalAudioDataset.PY_IMPACT.reset()

        # Create a new empty room.
        commands = [{"$type": "load_scene", "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]

        # Add the object.
        a = AudioInitData(name=name,
                          position={"x": 0, "y": 2, "z": 0})
        object_id, object_commands = a.get_commands()
        commands.extend(object_commands)
        commands.append({"$type": "set_reverb_space_simple",
                         "reverb_floor_material": "marble"})

        # Create the avatar.
        avatar_id = "a"
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 2, "z": 2},
                                               look_at={"x": 0, "y": 0, "z": 0},
                                               avatar_id=avatar_id))

        # Add an audio sensor to the avatar. Request the required output data.
        commands.extend([{"$type": "add_environ_audio_sensor",
                          "avatar_id": avatar_id},
                         {"$type": "send_rigidbodies",
                          "frequency": "always"},
                         {"$type": "send_collisions",
                          "enter": True,
                          "stay": True,
                          "exit": True,
                          "collision_types": ["obj", "env"]},
                         {"$type": "send_audio_sources",
                          "frequency": "always"}])
        resp = self.communicate(commands)

        # This must be sent to tell PyImpact which collisions to listen for.
        # `object_names` must include all objects in the scene that can produce audio.
        MinimalAudioDataset.PY_IMPACT.set_default_audio_info(object_names={object_id: name})

        # Start recording audio.
        AudioUtils.start(output_path=self.output_directory.joinpath(str(self.trial_num) + ".wav"))

        # Let the object fall.
        num_frames = 0
        done = False
        # Stop when either the simulation is done or there are too many frames.
        while not done and num_frames < 1000:
            # The trial is done when the object stops moving.
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "rigi":
                    rigi = Rigidbodies(resp[i])
                    for j in range(rigi.get_num()):
                        if rigi.get_id(j) == object_id:
                            if rigi.get_sleeping(j):
                                done = True
                                break
            # If there was a collision, get commands to generate a sound.
            commands = MinimalAudioDataset.PY_IMPACT.get_audio_commands(resp=resp,
                                                                        floor=MinimalAudioDataset.FLOOR,
                                                                        wall=MinimalAudioDataset.WALL,
                                                                        resonance_audio=True)
            resp = self.communicate(commands)

        # Wait for the audio to stop playing.
        audio_playing = True
        while audio_playing:
            audio_playing = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "audi":
                    audi = AudioSources(resp[i])
                    for j in range(audi.get_num()):
                        if audi.get_object_id(j) == object_id:
                            if audi.get_is_playing(j):
                                audio_playing = True
                                break
                    if not audio_playing:
                        if np.max(audi.get_samples()) > 0:
                            audio_playing = True
            resp = self.communicate([])

        # Stop recording audio.
        AudioUtils.stop()
        # Increment the trial counter.
        self.trial_num += 1


if __name__ == "__main__":
    c = MinimalAudioDataset(output_directory="D:/minimal_audio_dataset")
    c.run()
