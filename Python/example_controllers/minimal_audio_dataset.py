from pathlib import Path
from tdw.controller import Controller
from tdw.py_impact import PyImpact, AudioMaterial
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MinimalAudioDataset(Controller):
    """
    A minimal example of how to generate audio datasets.
    """

    # The PyImpact object.
    PY_IMPACT = PyImpact()
    # Audio materials for the floor and wall.
    FLOOR: AudioMaterial = AudioMaterial.wood_medium
    WALL: AudioMaterial = AudioMaterial.wood_medium

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.output_directory: Path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("minimal_audio_dataset")
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)
        print(f"Audio will be saved to: {self.output_directory}")
        # The trial number.
        self.trial_num: int = 0
        self.recorder: PhysicsAudioRecorder = PhysicsAudioRecorder(max_frames=1000)
        self.add_ons.append(self.recorder)
        self.communicate({"$type": "set_target_framerate",
                          "framerate": 60})

    def run(self) -> None:
        """
        Run a series of trials. Each trial generates a .wav file.
        """

        for name in ["iron_box", "rh10", "pepper"]:
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
                    TDWUtils.create_empty_room(12, 12),
                    {"$type": "set_reverb_space_simple",
                     "env": 0,
                     "reverb_floor_material": "marble"}]

        # Add the object.
        object_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name=name,
                                                    position={"x": 0, "y": 2, "z": 0},
                                                    object_id=object_id))

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
        self.recorder.start(output_path=self.output_directory.joinpath(str(self.trial_num) + ".wav"))

        # Let the object fall. Stop when either the simulation is done or there are too many frames.
        while self.recorder.recording:
            # If there was a collision, get commands to generate a sound.
            commands = MinimalAudioDataset.PY_IMPACT.get_audio_commands(resp=resp,
                                                                        floor=MinimalAudioDataset.FLOOR,
                                                                        wall=MinimalAudioDataset.WALL,
                                                                        resonance_audio=True)
            resp = self.communicate(commands)
        # Increment the trial counter.
        self.trial_num += 1


if __name__ == "__main__":
    c = MinimalAudioDataset()
    c.run()
