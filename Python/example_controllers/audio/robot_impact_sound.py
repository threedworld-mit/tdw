from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.robot import Robot
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Record an impact sound between an object and a robot.
"""

c = Controller()

# Add a camera and a robot.
avatar_id = "a"
robot = Robot(name="ur5")
camera = ThirdPersonCamera(avatar_id=avatar_id,
                           position={"x": 0, "y": 2, "z": 2},
                           look_at={"x": 0, "y": 0, "z": 0})
c.add_ons.extend([camera, robot])

# Initialize the scene.
c.communicate(TDWUtils.create_empty_room(6, 6))

# Wait for the robot to reach its initial pose.
while robot.joints_are_moving():
    c.communicate([])

# Initialize audio. Initialize PyImpact. Add an audio recorder.
floor_material = "tile"
audio_initializer = ResonanceAudioInitializer(avatar_id=avatar_id)
py_impact = PyImpact(initial_amp=0.5,
                     resonance_audio=True,
                     floor=ResonanceAudioInitializer.AUDIO_MATERIALS[floor_material])
recorder = PhysicsAudioRecorder()
c.add_ons.extend([audio_initializer, py_impact, recorder])

# Add an object above the robot.
c.communicate(c.get_add_physics_object(model_name="rh10",
                                       object_id=c.get_unique_id(),
                                       position={"x": 0, "y": 6, "z": 0}))

# Start recording audio.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("robot_impact_sound/output.wav")
print(f"Audio will be saved to: {path}")
recorder.start(path=path)

# Record audio until the object stops moving.
while recorder.recording:
    c.communicate([])
c.communicate({"$type": "terminate"})
