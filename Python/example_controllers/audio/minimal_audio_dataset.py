from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MinimalAudioDataset(Controller):
    """
    A minimal example of how to generate audio datasets.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.output_directory: Path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("minimal_audio_dataset")
        print(f"Audio will be saved to: {self.output_directory}")
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)
        print(f"Audio will be saved to: {self.output_directory}")
        # The trial number.
        self.trial_num: int = 0
        # Add a camera.
        avatar_id = "a"
        camera = ThirdPersonCamera(avatar_id=avatar_id,
                                   position={"x": 0, "y": 2, "z": 2},
                                   look_at={"x": 0, "y": 0, "z": 0})
        floor = "parquet"
        wall = "concrete"
        # Add an audio initializer.
        self.audio_initializer = ResonanceAudioInitializer(floor=floor,
                                                           front_wall=wall,
                                                           back_wall=wall,
                                                           left_wall=wall,
                                                           right_wall=wall)
        # Add PyImpact.
        self.initial_amp = 0.9
        self.py_impact: PyImpact = PyImpact(initial_amp=self.initial_amp,
                                            resonance_audio=True,
                                            floor=ResonanceAudioInitializer.AUDIO_MATERIALS[floor])
        # Add an audio recorder.
        self.recorder: PhysicsAudioRecorder = PhysicsAudioRecorder(max_frames=1000)

        self.add_ons.extend([camera, self.audio_initializer, self.py_impact, self.recorder])
        # Initialize the scene.
        self.communicate(TDWUtils.create_empty_room(8, 8))

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

        # Reset the audio.
        self.py_impact.reset(initial_amp=self.initial_amp)

        # Add the object.
        object_id = self.get_unique_id()
        self.communicate(self.get_add_physics_object(model_name=name,
                                                     position={"x": 0, "y": 2, "z": 0},
                                                     object_id=object_id))

        # Start recording audio.
        self.recorder.start(path=self.output_directory.joinpath(str(self.trial_num) + ".wav"))

        # Let the object fall. Stop when either the simulation is done or there are too many frames.
        while self.recorder.done:
            self.communicate([])
        # Increment the trial counter.
        self.trial_num += 1
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})


if __name__ == "__main__":
    c = MinimalAudioDataset()
    c.run()
