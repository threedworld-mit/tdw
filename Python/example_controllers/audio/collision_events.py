from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.collision_manager import CollisionManager
from tdw.add_ons.object_manager import ObjectManager
from tdw.physics_audio.collision_audio_event import CollisionAudioEvent
from tdw.physics_audio.collision_audio_type import CollisionAudioType
from tdw.physics_audio.object_audio_static import DEFAULT_OBJECT_AUDIO_STATIC_DATA

"""
Get collision audio event types without using PyImpact.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a",
                                       position={"x": 1, "y": 1.6, "z": -2},
                                       look_at={"x": 0, "y": 0.5, "z": 0}))
model_name = "vase_02"
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=c.get_unique_id()))
object_audio = DEFAULT_OBJECT_AUDIO_STATIC_DATA[model_name]
object_manager = ObjectManager(transforms=False, rigidbodies=True, bounds=False)
collision_manager = CollisionManager(enter=True, stay=True, exit=True, objects=False, environment=True)
c.add_ons.extend([collision_manager, object_manager])
c.communicate(commands)
previous_areas = dict()
for i in range(200):
    for object_id in collision_manager.env_collisions:
        event = CollisionAudioEvent(collision=collision_manager.env_collisions[object_id],
                                    object_0_dynamic=object_manager.rigidbodies[object_id],
                                    object_0_static=object_audio,
                                    object_1_dynamic=None,
                                    object_1_static=None,
                                    previous_areas=previous_areas)
        previous_areas = {object_id: event.area}
        if event.collision_type != CollisionAudioType.none:
            print(i, event.collision_type)
    c.communicate([])
c.communicate({"$type": "terminate"})
