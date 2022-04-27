from typing import List, Callable, Dict
import numpy as np
from tdw.add_ons.vr import VR
from tdw.vr_data.rig_type import RigType
from tdw.output_data import OutputData, StaticRigidbodies


class QuestHandTracking(VR):
    """
    Add a VR rig to the scene that uses Oculus Touch controllers.

    Make all non-kinematic objects graspable by the rig.

    Per-frame, update the positions of the VR rig, its hands, and its head, as well as which objects it is grasping and the controller button presses.
    """

    def __init__(self, set_graspable: bool = True, output_data: bool = False,
                 attach_avatar: bool = False, avatar_camera_width: int = 512, headset_aspect_ratio: float = 0.9,
                 headset_resolution_scale: float = 1.0, non_graspable: List[int] = None,
                 discrete_collision_detection_mode: bool = True):
        """
        :param set_graspable: If True, set all [non-kinematic objects](../../lessons/physx/physics_objects.md) and [composite sub-objects](../../lessons/semantic_states/composite_objects.md) as graspable by the VR rig.
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices.
        :param headset_resolution_scale: The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75
        :param non_graspable: A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param discrete_collision_detection_mode: If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW).
        """

        rig_type = RigType.quest_hand_tracking

        super().__init__(rig_type=rig_type, output_data=output_data, attach_avatar=attach_avatar,
                         avatar_camera_width=avatar_camera_width, headset_aspect_ratio=headset_aspect_ratio,
                         headset_resolution_scale=headset_resolution_scale)
        self._set_graspable: bool = set_graspable
        # Non-graspable objects.
        if non_graspable is None:
            self._non_graspable: List[int] = list()
        else:
            self._non_graspable: List[int] = non_graspable
        self._discrete_collision_detection_mode: bool = discrete_collision_detection_mode

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        if self._set_graspable:
            commands.append({"$type": "send_static_rigidbodies",
                             "frequency": "once"})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Make non-kinematic objects graspable.
        if self._set_graspable:
            self._set_graspable = False
   
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "srig":
                    static_rigidbodies = StaticRigidbodies(resp[i])
                    for j in range(static_rigidbodies.get_num()):
                        object_id = static_rigidbodies.get_id(j)
                        if not static_rigidbodies.get_kinematic(j):
                            # Make all non-kinematic objects graspable unless they are in `self._non_graspable`.
                            if object_id not in self._non_graspable:
                                self.commands.append({"$type": "set_vr_graspable",
                                                      "id": object_id})
                            # Set "discrete" collision detection mode for all non-kinematic objects.
                            if self._discrete_collision_detection_mode:
                                self.commands.append({"$type": "set_object_collision_detection_mode",
                                                      "id": object_id,
                                                      "mode": "discrete"})
                    break
        super().on_send(resp=resp)
   

    def reset(self, non_graspable: List[int] = None) -> None:
        """
        Reset the VR rig. Call this whenever a scene is reset.

        :param non_graspable: A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        """

        self._set_graspable = True
        if non_graspable is None:
            self._non_graspable = list()
        else:
            self._non_graspable = non_graspable
        super().reset()
