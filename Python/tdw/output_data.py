from abc import ABC, abstractmethod
from tdw.FBOutput import Vector3, Quaternion, PassMask, Color, MessageType, SimpleTransform, PathState
from tdw.FBOutput import SceneRegions as SceRegs
from tdw.FBOutput import Transforms as Trans
from tdw.FBOutput import Rigidbodies as Rigis
from tdw.FBOutput import Bounds as Bouns
from tdw.FBOutput import Images as Imags
from tdw.FBOutput import AvatarKinematic as AvKi
from tdw.FBOutput import AvatarNonKinematic as AvNoKi
from tdw.FBOutput import AvatarSimpleBody as AvSi
from tdw.FBOutput import SegmentationColors as Segs
from tdw.FBOutput import AvatarSegmentationColor as AvSC
from tdw.FBOutput import IsOnNavMesh as IsNM
from tdw.FBOutput import IdPassGrayscale as IdGS
from tdw.FBOutput import Collision as Col
from tdw.FBOutput import ImageSensors as ImSe
from tdw.FBOutput import CameraMatrices as CaMa
from tdw.FBOutput import IdPassSegmentationColors as IdSC
from tdw.FBOutput import FlexParticles as Flex
from tdw.FBOutput import VRRig as VR
from tdw.FBOutput import LogMessage as Log
from tdw.FBOutput import Meshes as Me
from tdw.FBOutput import Substructure as Sub
from tdw.FBOutput import Version as Ver
from tdw.FBOutput import EnvironmentCollision as EnvCol
from tdw.FBOutput import Volumes as Vol
from tdw.FBOutput import AudioSources as Audi
from tdw.FBOutput import Raycast as Ray
from tdw.FBOutput import Overlap as Over
from tdw.FBOutput import Containment as Cont
from tdw.FBOutput import NavMeshPath as Path
from tdw.FBOutput import StaticRobot as StRobo
from tdw.FBOutput import Keyboard as Key
from tdw.FBOutput import Magnebot as Mag
from tdw.FBOutput import ScreenPosition as Screen
from tdw.FBOutput import TriggerCollision as Trigger
from tdw.FBOutput import LocalTransforms as LocalTran
from tdw.FBOutput import DriveAxis, JointType
from tdw.FBOutput import QuitSignal as QuitSig
from tdw.FBOutput import MagnebotWheels as MWheels
from tdw.FBOutput import Occlusion as Occl
from tdw.FBOutput import Lights as Lites
from tdw.FBOutput import Categories as Cats
from tdw.FBOutput import StaticRigidbodies as StatRig
from tdw.FBOutput import RobotJointVelocities as RoJoVe
from tdw.FBOutput import StaticEmptyObjects as StaticEmpty
from tdw.FBOutput import DynamicEmptyObjects as DynamicEmpty
from tdw.FBOutput import OculusTouchButtons as OculusTouch
from tdw.FBOutput import StaticOculusTouch as StatOc
from tdw.FBOutput import StaticCompositeObjects as StatComp
from tdw.FBOutput import DynamicCompositeObjects as DynComp
from tdw.FBOutput import AudioSourceDone as AudDone
from tdw.FBOutput import ObiParticles as ObiP
from tdw.FBOutput import ObjectColliderIntersection as ObjColInt
from tdw.FBOutput import EnvironmentColliderIntersection as EnvColInt
from tdw.FBOutput import Mouse as Mous
from tdw.FBOutput import TransformMatrices as TranMat
from tdw.FBOutput import AvatarTransformMatrices as AvTranMat
from tdw.FBOutput import DynamicRobots as DynRob
from tdw.FBOutput import FieldOfView as Fov
from tdw.FBOutput import Replicants as Repl
from tdw.FBOutput import LeapMotion as Leap
from tdw.FBOutput import Framerate as Frame
from tdw.FBOutput import OccupancyMap as Occ
from tdw.FBOutput import EulerAngles as Eulers
from tdw.FBOutput import Drones as Dro
from tdw.FBOutput import ReplicantSegmentationColors as RepSepCo
from tdw.vr_data.oculus_touch_button import OculusTouchButton
from tdw.container_data.container_tag import ContainerTag
from tdw.replicant.action_status import ActionStatus
import numpy as np
from typing import Tuple, Optional, List


class OutputDataUndefinedError(Exception):
    pass


class OutputData(object):
    def __init__(self, b):
        self.bytes = bytearray(b)
        self.data = self.get_data()

    def get_data(self):
        raise OutputDataUndefinedError("Undefined!")

    @staticmethod
    def get_data_type_id(b: bytes) -> str:
        """
        Returns the ID of the serialized object.
        :param b: A byte array.
        """

        return b[4:8].decode('utf-8')

    @staticmethod
    def _get_vector3(constructor) -> Tuple[float, float, float]:
        """
        Returns x, y, and z values of a Vector3, given a constructor.

        :param constructor: A constructor that accepts 1 parameter of type Vector3.
        """

        return OutputData._get_xyz(constructor(Vector3.Vector3()))

    @staticmethod
    def _get_xyz(vector3: Vector3) -> Tuple[float, float, float]:
        """
        returns the x, y, and z values of a Vector3, given the Vector3 object.

        :param vector3: The Vector3 object.
        """

        return vector3.X(), vector3.Y(), vector3.Z()

    @staticmethod
    def _get_quaternion(constructor) -> Tuple[float, float, float, float]:
        """
        Returns x, y, z, and w values of a Quaternion, given a constructor.

        :param constructor: A constructor that accepts 1 parameter of type Quaternion.
        """

        return OutputData._get_xyzw(constructor(Quaternion.Quaternion()))

    @staticmethod
    def _get_xyzw(quaternion: Quaternion) -> Tuple[float, float, float, float]:
        """
        returns the x, y, and z values of a Quaternion, given the Quaternion object.

        :param quaternion: The Quaternion object.
        """

        return quaternion.X(), quaternion.Y(), quaternion.Z(), quaternion.W()

    @staticmethod
    def _get_color(constructor) -> Tuple[float, float, float]:
        """
        Returns the r, g, and b values of a Color, given a constructor.

        :param constructor: A constructor that accepts 1 parameter of type Color.
        """

        return OutputData._get_rgb(constructor(Color.Color()))

    @staticmethod
    def _get_rgb(color: Color) -> Tuple[float, float, float]:
        """
        returns the r, g, and b values of a Color, given the Color object.

        :param color: The Color object.
        """
        return color.R(), color.G(), color.B()


class SceneRegions(OutputData):
    def get_data(self) -> SceRegs.SceneRegions:
        return SceRegs.SceneRegions.GetRootAsSceneRegions(self.bytes, 0)

    def get_center(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Regions(index).Center)

    def get_bounds(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Regions(index).Bounds)

    def get_id(self, index: int) -> int:
        return self.data.Regions(index).Id()

    def get_num(self) -> int:
        return self.data.RegionsLength()


class Transforms(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._positions = self.data.PositionsAsNumpy().reshape(-1, 3)
        self._rotations = self.data.RotationsAsNumpy().reshape(-1, 4)
        self._forwards = self.data.ForwardsAsNumpy().reshape(-1, 3)

    def get_data(self) -> Trans.Transforms:
        return Trans.Transforms.GetRootAsTransforms(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_position(self, index: int) -> np.ndarray:
        return self._positions[index]

    def get_forward(self, index: int) -> np.ndarray:
        return self._forwards[index]

    def get_rotation(self, index: int) -> np.ndarray:
        return self._rotations[index]


class Rigidbodies(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._velocities = self.data.VelocitiesAsNumpy().reshape(-1, 3)
        self._angular_velocities = self.data.AngularVelocitiesAsNumpy().reshape(-1, 3)
        self._sleeping = self.data.SleepingsAsNumpy()

    def get_data(self) -> Rigis.Rigidbodies:
        return Rigis.Rigidbodies.GetRootAsRigidbodies(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_velocity(self, index: int) -> np.ndarray:
        return self._velocities[index]

    def get_angular_velocity(self, index: int) -> np.ndarray:
        return self._angular_velocities[index]

    def get_sleeping(self, index: int) -> bool:
        return bool(self._sleeping[index])


class StaticRigidbodies(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._physics_values = self.data.PhysicsValuesAsNumpy().reshape(-1, 4)
        self._kinematic = self.data.KinematicAsNumpy()

    def get_data(self) -> StatRig.StaticRigidbodies:
        return StatRig.StaticRigidbodies.GetRootAsStaticRigidbodies(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_mass(self, index: int) -> float:
        return float(self._physics_values[index][0])

    def get_kinematic(self, index: int) -> bool:
        return bool(self._kinematic[index])

    def get_dynamic_friction(self, index: int) -> float:
        return float(self._physics_values[index][1])

    def get_static_friction(self, index: int) -> float:
        return float(self._physics_values[index][2])

    def get_bounciness(self, index: int) -> float:
        return float(self._physics_values[index][3])


class Bounds(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._bounds_positions = self.data.BoundPositionsAsNumpy().reshape(len(self._ids), 7, 3)

    def get_data(self) -> Bouns.Bounds:
        return Bouns.Bounds.GetRootAsBounds(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_front(self, index: int) -> np.ndarray:
        return self._bounds_positions[index][0]

    def get_back(self, index: int) -> np.ndarray:
        return self._bounds_positions[index][1]

    def get_left(self, index: int) -> np.ndarray:
        return self._bounds_positions[index][3]

    def get_right(self, index: int) -> np.ndarray:
        return self._bounds_positions[index][2]

    def get_top(self, index: int) -> np.ndarray:
        return self._bounds_positions[index][4]

    def get_bottom(self, index: int) -> np.ndarray:
        return self._bounds_positions[index][5]

    def get_center(self, index: int) -> np.ndarray:
        return self._bounds_positions[index][6]


class Images(OutputData):
    PASS_MASKS = {PassMask.PassMask._img: "_img",
                  PassMask.PassMask._id: "_id",
                  PassMask.PassMask._category: "_category",
                  PassMask.PassMask._mask: "_mask",
                  PassMask.PassMask._depth: "_depth",
                  PassMask.PassMask._normals: "_normals",
                  PassMask.PassMask._flow: "_flow",
                  PassMask.PassMask._depth_simple: "_depth_simple",
                  PassMask.PassMask._albedo: "_albedo"
                  }

    def get_data(self) -> Imags.Images:
        return Imags.Images.GetRootAsImages(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_num_passes(self) -> int:
        return self.data.PassesLength()

    def get_pass_mask(self, index: int) -> str:
        return Images.PASS_MASKS[self.data.Passes(index).PassMask()]

    def get_image(self, index: int) -> np.ndarray:
        return self.data.Passes(index).ImageAsNumpy()

    def get_extension(self, index: int) -> str:
        return "png" if self.data.Passes(index).Extension() == 1 else "jpg"

    def get_width(self) -> int:
        return self.data.Width()

    def get_height(self) -> int:
        return self.data.Height()


class AvatarKinematic(OutputData):
    def get_data(self) -> AvKi.AvatarKinematic:
        return AvKi.AvatarKinematic.GetRootAsAvatarKinematic(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.Id().decode('utf-8')

    def get_position(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Position())

    def get_rotation(self) -> Tuple[float, float, float, float]:
        return OutputData._get_xyzw(self.data.Rotation())

    def get_forward(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Forward())


class AvatarNonKinematic(AvatarKinematic):
    def get_data(self) -> AvNoKi.AvatarNonKinematic:
        return AvNoKi.AvatarNonKinematic.GetRootAsAvatarNonKinematic(self.bytes, 0)

    def get_velocity(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Velocity())

    def get_angular_velocity(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.AngularVelocity())

    def get_mass(self) -> float:
        return self.data.Mass()

    def get_sleeping(self) -> bool:
        return self.data.Sleeping()


class AvatarSimpleBody(AvatarNonKinematic):
    def get_data(self) -> AvSi.AvatarSimpleBody:
        return AvSi.AvatarSimpleBody.GetRootAsAvatarSimpleBody(self.bytes, 0)

    def get_visible_body(self) -> str:
        return self.data.VisibleBody().decode('utf-8')


class SegmentationColors(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._colors = self.data.ColorsAsNumpy().reshape(-1, 3)

    def get_data(self) -> Segs.SegmentationColors:
        return Segs.SegmentationColors.GetRootAsSegmentationColors(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_object_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_object_color(self, index: int) -> np.ndarray:
        return self._colors[index]

    def get_object_name(self, index: int) -> str:
        return self.data.Names(index).decode('utf-8')

    def get_object_category(self, index: int) -> str:
        return self.data.Categories(index).decode('utf-8')


class AvatarSegmentationColor(OutputData):
    def get_data(self) -> AvSC.AvatarSegmentationColor:
        return AvSC.AvatarSegmentationColor.GetRootAsAvatarSegmentationColor(self.bytes, 0)

    def get_id(self) -> str:
        return self.data.Id().decode('utf-8')

    def get_segmentation_color(self) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.SegmentationColor())


class IsOnNavMesh(OutputData):
    def get_data(self) -> IsNM.IsOnNavMesh:
        return IsNM.IsOnNavMesh.GetRootAsIsOnNavMesh(self.bytes, 0)

    def get_position(self) -> np.ndarray:
        return self.data.PositionAsNumpy()

    def get_is_on(self) -> bool:
        return self.data.IsOn()

    def get_id(self) -> int:
        return self.data.Id()


class IdPassGrayscale(OutputData):
    def get_data(self) -> IdGS.IdPassGrayscale:
        return IdGS.IdPassGrayscale.GetRootAsIdPassGrayscale(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_grayscale(self) -> float:
        return self.data.Grayscale()


class Collision(OutputData):
    def get_data(self) -> Col.Collision:
        return Col.Collision.GetRootAsCollision(self.bytes, 0)

    def get_collider_id(self) -> int:
        return self.data.ColliderId()

    def get_collidee_id(self) -> int:
        return self.data.CollideeId()

    def get_relative_velocity(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.RelativeVelocity())

    def get_impulse(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Impulse())

    def get_state(self) -> str:
        state = self.data.State()
        if state == 1:
            return "enter"
        elif state == 2:
            return "stay"
        else:
            return "exit"

    def get_num_contacts(self) -> int:
        return self.data.ContactsLength()

    def get_contact_normal(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Contacts(index).Normal)

    def get_contact_point(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Contacts(index).Point)


class ImageSensors(OutputData):
    def get_data(self) -> ImSe.ImageSensors:
        return ImSe.ImageSensors.GetRootAsImageSensors(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_num_sensors(self) -> int:
        return self.data.SensorsLength()

    def get_sensor_name(self, index: int) -> str:
        return self.data.Sensors(index).Name().decode('utf-8')

    def get_sensor_on(self, index: int) -> bool:
        return self.data.Sensors(index).IsOn()

    def get_sensor_rotation(self, index: int) -> Tuple[float, float, float, float]:
        return OutputData._get_xyzw(self.data.Sensors(index).Rotation())

    def get_sensor_forward(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Sensors(index).Forward())

    def get_sensor_field_of_view(self, index: int) -> float:
        return self.data.Sensors(index).FieldOfView()


class CameraMatrices(OutputData):
    def get_data(self) -> CaMa.CameraMatrices:
        return CaMa.CameraMatrices.GetRootAsCameraMatrices(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_projection_matrix(self) -> np.ndarray:
        return self.data.ProjectionMatrixAsNumpy()

    def get_camera_matrix(self) -> np.ndarray:
        return self.data.CameraMatrixAsNumpy()


class IdPassSegmentationColors(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._colors: np.ndarray = self.data.SegmentationColorsAsNumpy().reshape(-1, 3)

    def get_data(self) -> IdSC.IdPassSegmentationColors:
        return IdSC.IdPassSegmentationColors.GetRootAsIdPassSegmentationColors(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_num_segmentation_colors(self) -> int:
        return self._colors.shape[0]

    def get_segmentation_color(self, index: int) -> np.ndarray:
        return self._colors[index]


class FlexParticles(OutputData):
    def get_data(self) -> Flex.FlexParticles:
        return Flex.FlexParticles.GetRootAsFlexParticles(self.bytes, 0)

    def get_num_objects(self) -> int:
        return self.data.ObjectsLength()

    def get_particles(self, index: int) -> np.ndarray:
        return self.data.Objects(index).ParticlesAsNumpy().view(dtype=np.float32).reshape(-1, 4)

    def get_velocities(self, index: int) -> np.ndarray:
        return self.data.Objects(index).VelocitiesAsNumpy().view(dtype=np.float32).reshape(-1, 3)

    def get_id(self, index: int) -> int:
        return self.data.Objects(index).Id()


class VRRig(OutputData):
    def get_data(self) -> VR.VRRig:
        return VR.VRRig.GetRootAsVRRig(self.bytes, 0)

    def get_position(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Position())

    def get_rotation(self) -> Tuple[float, float, float, float]:
        return OutputData._get_xyzw(self.data.Rotation())

    def get_forward(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Forward())

    def _get_simple_transform(self, t: int) -> SimpleTransform:
        if t == 0:
            return self.data.LeftHand()
        elif t == 1:
            return self.data.RightHand()
        elif t == 2:
            return self.data.Head()
        else:
            raise Exception("Not defined: " + str(t))

    def _get_hand_position(self, is_left: bool) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self._get_simple_transform(0 if is_left else 1).Position)

    def _get_hand_rotation(self, is_left: bool) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self._get_simple_transform(0 if is_left else 1).Rotation)

    def _get_hand_forward(self, is_left: bool) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self._get_simple_transform(0 if is_left else 1).Forward)

    def get_left_hand_position(self) -> Tuple[float, float, float]:
        return self._get_hand_position(True)

    def get_left_hand_rotation(self) -> Tuple[float, float, float, float]:
        return self._get_hand_rotation(True)

    def get_left_hand_forward(self) -> Tuple[float, float, float]:
        return self._get_hand_forward(True)

    def get_right_hand_position(self) -> Tuple[float, float, float]:
        return self._get_hand_position(False)

    def get_right_hand_rotation(self) -> Tuple[float, float, float, float]:
        return self._get_hand_rotation(False)

    def get_right_hand_forward(self) -> Tuple[float, float, float]:
        return self._get_hand_forward(False)

    def get_head_position(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self._get_simple_transform(2).Position)

    def get_head_rotation(self) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self._get_simple_transform(2).Rotation)

    def get_head_forward(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self._get_simple_transform(2).Forward)

    def get_held_left(self) -> np.ndarray:
        return self.data.HeldLeftAsNumpy()

    def get_held_right(self) -> np.ndarray:
        return self.data.HeldRightAsNumpy()


class OculusTouchButtons(OutputData):
    BUTTONS = [b for b in OculusTouchButton]

    def get_data(self) -> OculusTouch.OculusTouchButtons:
        return OculusTouch.OculusTouchButtons.GetRootAsOculusTouchButtons(self.bytes, 0)

    def get_left(self) -> List[OculusTouchButton]:
        return self._get_buttons(v=self.data.Left())

    def get_right(self) -> List[OculusTouchButton]:
        return self._get_buttons(v=self.data.Right())

    def get_left_axis(self) -> np.ndarray:
        return self.data.LeftAxisAsNumpy()

    def get_right_axis(self) -> np.ndarray:
        return self.data.RightAxisAsNumpy()

    @staticmethod
    def _get_buttons(v: int) -> List[OculusTouchButton]:
        return [OculusTouchButtons.BUTTONS[i] for (i, b) in enumerate(OculusTouchButtons.BUTTONS) if v & (1 << i) != 0]


class StaticOculusTouch(OutputData):
    def get_data(self) -> StatOc.StaticOculusTouch:
        return StatOc.StaticOculusTouch.GetRootAsStaticOculusTouch(self.bytes, 0)

    def get_body_id(self) -> int:
        return self.data.BodyId()

    def get_left_hand_id(self) -> int:
        return self.data.LeftHandId()

    def get_right_hand_id(self) -> int:
        return self.data.RightHandId()

    def get_human_hands(self) -> bool:
        return self.data.HumanHands()


class LogMessage(OutputData):
    LOG_TYPES = {MessageType.MessageType.error: "error",
                 MessageType.MessageType.warning: "warning",
                 MessageType.MessageType.message: "message",
                 }

    def get_data(self) -> Log.LogMessage:
        return Log.LogMessage.GetRootAsLogMessage(self.bytes, 0)

    def get_message(self) -> str:
        return self.data.Message().decode('utf-8')

    def get_message_type(self) -> str:
        return LogMessage.LOG_TYPES[self.data.MessageType()]

    def get_object_type(self) -> str:
        return self.data.ObjectType().decode('utf-8')


class Meshes(OutputData):
    def get_data(self) -> Me.Meshes:
        return Me.Meshes.GetRootAsMeshes(self.bytes, 0)

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_vertices(self, index: int) -> np.ndarray:
        return self.data.Objects(index).VerticesAsNumpy().view(dtype=np.float32).reshape(-1, 3)

    def get_triangles(self, index: int) -> np.ndarray:
        return self.data.Objects(index).TrianglesAsNumpy().view(dtype=np.int32).reshape(-1, 3)


class Substructure(OutputData):
    def get_data(self) -> Sub.Substructure:
        return Sub.Substructure.GetRootAsSubstructure(self.bytes, 0)

    def get_num_sub_objects(self) -> int:
        return self.data.SubObjectsLength()

    def get_sub_object_name(self, index: int) -> str:
        return self.data.SubObjects(index).Name().decode('utf-8')

    def get_num_sub_object_materials(self, index: int) -> int:
        return self.data.SubObjects(index).MaterialsLength()

    def get_sub_object_material(self, index: int, material_index: int) -> str:
        return self.data.SubObjects(index).Materials(material_index).decode('utf-8')


class Version(OutputData):
    def get_data(self) -> Ver.Version:
        return Ver.Version.GetRootAsVersion(self.bytes, 0)

    def get_unity_version(self) -> str:
        return self.data.Unity().decode('utf-8')

    def get_tdw_version(self) -> str:
        return self.data.Tdw().decode('utf-8')

    def get_standalone(self) -> bool:
        return self.data.Standalone()


class EnvironmentCollision(OutputData):
    def get_data(self) -> EnvCol.EnvironmentCollision:
        return EnvCol.EnvironmentCollision.GetRootAsEnvironmentCollision(self.bytes, 0)

    def get_object_id(self) -> int:
        return self.data.ObjectId()

    def get_state(self) -> str:
        state = self.data.State()
        if state == 1:
            return "enter"
        elif state == 2:
            return "stay"
        else:
            return "exit"

    def get_num_contacts(self) -> int:
        return self.data.ContactsLength()

    def get_contact_normal(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Contacts(index).Normal)

    def get_contact_point(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Contacts(index).Point)

    def get_floor(self) -> bool:
        return self.data.Floor()


class Volumes(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids: np.ndarray = self.data.IdsAsNumpy()
        self._volumes: np.ndarray = self.data.VolumeAsNumpy()

    def get_data(self) -> Vol.Volumes:
        return Vol.Volumes.GetRootAsVolumes(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_object_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_volume(self, index: int) -> float:
        return float(self._volumes[index])


class AudioSources(OutputData):
    def get_data(self) -> Audi.AudioSources:
        return Audi.AudioSources.GetRootAsAudioSources(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_is_playing(self, index: int) -> bool:
        return self.data.Objects(index).IsPlaying()

    def get_samples(self) -> np.ndarray:
        return self.data.SamplesAsNumpy()


class AudioSourceDone(OutputData):
    def get_data(self) -> AudDone.AudioSourceDone:
        return AudDone.AudioSourceDone.GetRootAsAudioSourceDone(self.bytes, 0)

    def get_id(self) -> int:
        return self.data.Id()


class Raycast(OutputData):
    def get_data(self) -> Ray.Raycast:
        return Ray.Raycast.GetRootAsRaycast(self.bytes, 0)

    def get_raycast_id(self) -> int:
        return self.data.RaycastId()

    def get_hit(self) -> bool:
        return self.data.Hit()

    def get_hit_object(self) -> bool:
        return self.data.HitObject()

    def get_object_id(self) -> Optional[int]:
        return self.data.ObjectId()

    def get_normal(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Normal())

    def get_point(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Point())


class Overlap(OutputData):
    def get_data(self) -> Over.Overlap:
        return Over.Overlap.GetRootAsOverlap(self.bytes, 0)

    def get_id(self) -> int:
        return self.data.Id()

    def get_object_ids(self) -> np.ndarray:
        return self.data.ObjectIdsAsNumpy()

    def get_env(self) -> bool:
        return self.data.Env()

    def get_walls(self) -> bool:
        return self.data.Walls()


class Containment(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids: np.ndarray = self.data.IdsAsNumpy()

    def get_data(self):
        return Cont.Containment.GetRootAsContainment(self.bytes, 0)

    def get_object_id(self) -> int:
        return int(self._ids[0])

    def get_container_id(self) -> int:
        return int(self._ids[1])

    def get_tag(self) -> ContainerTag:
        return ContainerTag(self.data.Tag())

    def get_overlap_ids(self) -> np.ndarray:
        return self.data.OverlapIdsAsNumpy()

    def get_env(self) -> bool:
        return self.data.Env()

    def get_walls(self) -> bool:
        return self.data.Walls()


class NavMeshPath(OutputData):
    _STATES = {PathState.PathState.complete: "complete",
               PathState.PathState.invalid: "invalid",
               PathState.PathState.partial: "partial"}

    def get_data(self) -> Path.NavMeshPath:
        return Path.NavMeshPath.GetRootAsNavMeshPath(self.bytes, 0)

    def get_state(self) -> str:
        return NavMeshPath._STATES[self.data.State()]

    def get_path(self) -> np.ndarray:
        return self.data.PathAsNumpy().view(dtype=np.float32).reshape(-1, 3)

    def get_id(self) -> int:
        return int(self.data.Id())


class StaticRobot(OutputData):
    _AXES = {DriveAxis.DriveAxis.x: "x",
             DriveAxis.DriveAxis.y: "y",
             DriveAxis.DriveAxis.z: "z"}
    _JOINT_TYPES = {JointType.JointType.revolute: "revolute",
                    JointType.JointType.spherical: "spherical",
                    JointType.JointType.prismatic: "prismatic",
                    JointType.JointType.fixed_joint: "fixed_joint"}

    def get_data(self) -> StRobo.StaticRobot:
        return StRobo.StaticRobot.GetRootAsStaticRobot(self.bytes, 0)

    def get_id(self) -> int:
        return self.data.Id()

    def get_num_joints(self) -> int:
        return self.data.JointsLength()

    def get_joint_id(self, index: int) -> int:
        return self.data.Joints(index).Id()

    def get_joint_segmentation_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.Joints(index).SegmentationColor())

    def get_joint_mass(self, index: int) -> float:
        return self.data.Joints(index).Mass()

    def get_is_joint_immovable(self, index: int) -> bool:
        return self.data.Joints(index).Immovable()

    def get_is_joint_root(self, index: int) -> bool:
        return self.data.Joints(index).Root()

    def get_joint_parent_id(self, index: int) -> int:
        return self.data.Joints(index).ParentId()

    def get_joint_name(self, index: int) -> str:
        return self.data.Joints(index).Name().decode('utf-8')

    def get_joint_type(self, index: int) -> str:
        return StaticRobot._JOINT_TYPES[self.data.Joints(index).JointType()]

    def get_num_joint_drives(self, index: int) -> int:
        return self.data.Joints(index).DrivesLength()

    def get_joint_drive_axis(self, index: int, drive_index: int) -> str:
        return StaticRobot._AXES[self.data.Joints(index).Drives(drive_index).Axis()]

    def get_joint_drive_limits(self, index: int, drive_index: int) -> bool:
        return self.data.Joints(index).Drives(drive_index).Limits()

    def get_joint_drive_lower_limit(self, index: int, drive_index: int) -> float:
        return self.data.Joints(index).Drives(drive_index).LowerLimit()

    def get_joint_drive_upper_limit(self, index: int, drive_index: int) -> float:
        return self.data.Joints(index).Drives(drive_index).UpperLimit()

    def get_joint_drive_force_limit(self, index: int, drive_index: int) -> float:
        return self.data.Joints(index).Drives(drive_index).ForceLimit()

    def get_joint_drive_stiffness(self, index: int, drive_index: int) -> float:
        return self.data.Joints(index).Drives(drive_index).Stiffness()

    def get_joint_drive_damping(self, index: int, drive_index: int) -> float:
        return self.data.Joints(index).Drives(drive_index).Damping()

    def get_num_non_moving(self) -> int:
        return self.data.NonMovingLength()

    def get_non_moving_id(self, index: int) -> int:
        return self.data.NonMoving(index).Id()

    def get_non_moving_name(self, index: int) -> str:
        return self.data.NonMoving(index).Name().decode('utf-8')

    def get_non_moving_segmentation_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.NonMoving(index).SegmentationColor())

    def get_joint_indices(self) -> np.ndarray:
        return self.data.JointIndicesAsNumpy().reshape(-1, 2)

    def get_robot_index(self) -> int:
        return self.data.Index()


class RobotJointVelocities(OutputData):
    def get_data(self) -> RoJoVe.RobotJointVelocities:
        return RoJoVe.RobotJointVelocities.GetRootAsRobotJointVelocities(self.bytes, 0)

    def get_id(self) -> int:
        return self.data.Id()

    def get_num_joints(self) -> int:
        return self.data.JointsLength()

    def get_joint_id(self, index: int) -> int:
        return self.data.Joints(index).Id()

    def get_joint_velocity(self, index: int) -> np.ndarray:
        return self.data.Joints(index).VelocityAsNumpy()

    def get_joint_angular_velocity(self, index: int) -> np.ndarray:
        return self.data.Joints(index).AngularVelocityAsNumpy()

    def get_joint_sleeping(self, index: int) -> bool:
        return self.data.Joints(index).Sleeping()


class DynamicRobots(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._immovable = self.data.ImmovableAsNumpy()
        self._transforms = self.data.TransformsAsNumpy().reshape(-1, 10)
        self._joints = self.data.JointsAsNumpy().reshape(-1, 2, 3)
        self._sleeping = self.data.SleepingAsNumpy()

    def get_data(self) -> DynRob.DynamicRobots:
        return DynRob.DynamicRobots.GetRootAsDynamicRobots(self.bytes, 0)

    def get_immovable(self, index: int) -> bool:
        return bool(self._immovable[index])

    def get_robot_position(self, index: int) -> np.ndarray:
        return self._transforms[index][:3]

    def get_robot_rotation(self, index: int) -> np.ndarray:
        return self._transforms[index][3:7]

    def get_robot_forward(self, index: int) -> np.ndarray:
        return self._transforms[index][7:]

    def get_joint_position(self, index: int) -> np.ndarray:
        return self._joints[index][0]

    def get_joint_angles(self, index: int) -> np.ndarray:
        return np.degrees(self._joints[index][1])

    def get_joint_sleeping(self, index: int) -> bool:
        return bool(self._sleeping[index])


class Keyboard(OutputData):
    def get_data(self) -> Key.Keyboard:
        return Key.Keyboard.GetRootAsKeyboard(self.bytes, 0)

    def get_num_pressed(self) -> int:
        return self.data.PressedLength()

    def get_pressed(self, index: int) -> str:
        return self.data.Pressed(index).decode('utf-8')

    def get_num_held(self) -> int:
        return self.data.HeldLength()

    def get_held(self, index: int) -> str:
        return self.data.Held(index).decode('utf-8')

    def get_num_released(self) -> int:
        return self.data.ReleasedLength()

    def get_released(self, index: int) -> str:
        return self.data.Released(index).decode('utf-8')


class ScreenPosition(OutputData):
    def get_data(self) -> Screen.ScreenPosition:
        return Screen.ScreenPosition.GetRootAsScreenPosition(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_id(self) -> int:
        return self.data.Id()

    def get_screen(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Screen())

    def get_world(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.World())


class Magnebot(OutputData):
    def get_data(self) -> Mag.Magnebot:
        return Mag.Magnebot.GetRootAsMagnebot(self.bytes, 0)

    def get_id(self) -> int:
        return self.data.Id()

    def get_held_left(self) -> np.ndarray:
        return self.data.HeldLeftAsNumpy()

    def get_held_right(self) -> np.ndarray:
        return self.data.HeldRightAsNumpy()

    def get_top(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Top())


class TriggerCollision(OutputData):
    def get_data(self) -> Trigger.TriggerCollision:
        return Trigger.TriggerCollision.GetRootAsTriggerCollision(self.bytes, 0)

    def get_collidee_id(self) -> int:
        return self.data.CollideeId()

    def get_collider_id(self) -> int:
        return self.data.ColliderId()

    def get_trigger_id(self) -> int:
        return self.data.TriggerId()

    def get_state(self) -> str:
        state = self.data.State()
        if state == 1:
            return "enter"
        elif state == 2:
            return "stay"
        else:
            return "exit"


class LocalTransforms(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._positions = self.data.PositionsAsNumpy().reshape(-1, 3)
        self._rotations = self.data.RotationsAsNumpy().reshape(-1, 4)
        self._forwards = self.data.ForwardsAsNumpy().reshape(-1, 3)
        self._euler_angles = self.data.EulerAnglesAsNumpy().reshape(-1, 3)

    def get_data(self) -> LocalTran.LocalTransforms:
        return LocalTran.LocalTransforms.GetRootAsLocalTransforms(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_position(self, index: int) -> np.ndarray:
        return self._positions[index]

    def get_forward(self, index: int) -> np.ndarray:
        return self._forwards[index]

    def get_rotation(self, index: int) -> np.ndarray:
        return self._rotations[index]

    def get_euler_angles(self, index: int) -> np.ndarray:
        return self._euler_angles[index]


class QuitSignal(OutputData):
    def get_data(self) -> QuitSig.QuitSignal:
        return QuitSig.QuitSignal.GetRootAsQuitSignal(self.bytes, 0)

    def get_ok(self) -> bool:
        return self.data.Ok()


class MagnebotWheels(OutputData):
    def get_data(self) -> MWheels.MagnebotWheels:
        return MWheels.MagnebotWheels.GetRootAsMagnebotWheels(self.bytes, 0)

    def get_id(self) -> int:
        return self.data.Id()

    def get_success(self) -> bool:
        return self.data.Success()


class Occlusion(OutputData):
    def get_data(self) -> Occl.Occlusion:
        return Occl.Occlusion.GetRootAsOcclusion(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_occluded(self) -> float:
        return self.data.Occluded()


class Lights(OutputData):
    def get_data(self) -> Lites.Lights:
        return Lites.Lights.GetRootAsLights(self.bytes, 0)

    def get_num_directional_lights(self) -> int:
        return self.data.DirectionalLightsLength()

    def get_directional_light_intensity(self, index: int) -> float:
        return self.data.DirectionalLights(index).Intensity()

    def get_directional_light_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.DirectionalLights(index).Color())

    def get_directional_light_rotation(self, index: int) -> Tuple[float, float, float, float]:
        return OutputData._get_xyzw(self.data.DirectionalLights(index).Rotation())

    def get_num_point_lights(self) -> int:
        return self.data.PointLightsLength()

    def get_point_light_intensity(self, index: int) -> float:
        return self.data.PointLights(index).Intensity()

    def get_point_light_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.PointLights(index).Color())

    def get_point_light_position(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.PointLights(index).Position())

    def get_point_light_range(self, index) -> float:
        return self.data.PointLights(index).Range()


class Categories(OutputData):
    def get_data(self) -> Cats.Categories:
        return Cats.Categories.GetRootAsCategories(self.bytes, 0)

    def get_num_categories(self) -> int:
        return self.data.CategoryDataLength()

    def get_category_name(self, index: int) -> str:
        return self.data.CategoryData(index).Name().decode('utf-8')

    def get_category_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.CategoryData(index).Color())


class StaticEmptyObjects(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids: np.ndarray = self.data.IdsAsNumpy().reshape(-1, 2)

    def get_data(self) -> StaticEmpty.StaticEmptyObjects:
        return StaticEmpty.StaticEmptyObjects.GetRootAsStaticEmptyObjects(self.bytes, 0)

    def get_num(self) -> int:
        return int(self._ids.shape[0])

    def get_object_id(self, index: int) -> int:
        return int(self._ids[index][0])

    def get_empty_object_id(self, index: int) -> int:
        return int(self._ids[index][1])


class DynamicEmptyObjects(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._positions = self.data.PositionsAsNumpy().view(dtype=np.float32).reshape(-1, 3)

    def get_data(self) -> DynamicEmpty.DynamicEmptyObjects:
        return DynamicEmpty.DynamicEmptyObjects.GetRootAsDynamicEmptyObjects(self.bytes, 0)

    def get_num(self) -> int:
        return int(self._positions.shape[0])

    def get_position(self, index: int) -> np.ndarray:
        return self._positions[index]


class ObjectColliderIntersection(OutputData):
    def get_data(self) -> ObjColInt.ObjectColliderIntersection:
        return ObjColInt.ObjectColliderIntersection.GetRootAsObjectColliderIntersection(self.bytes, 0)

    def get_object_id_a(self) -> int:
        return self.data.ObjectIdA()

    def get_object_id_b(self) -> int:
        return self.data.ObjectIdB()

    def get_distance(self) -> float:
        return self.data.Distance()

    def get_direction(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Direction())


class EnvironmentColliderIntersection(OutputData):
    def get_data(self) -> EnvColInt.EnvironmentColliderIntersection:
        return EnvColInt.EnvironmentColliderIntersection.GetRootAsEnvironmentColliderIntersection(self.bytes, 0)

    def get_object_id(self) -> int:
        return self.data.ObjectId()

    def get_distance(self) -> float:
        return self.data.Distance()

    def get_direction(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Direction())


class StaticCompositeObjects(OutputData):
    def get_data(self) -> StatComp.StaticCompositeObjects:
        return StatComp.StaticCompositeObjects.GetRootAsStaticCompositeObjects(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_num_non_machines(self, index: int) -> int:
        return self.data.Objects(index).NonMachinesLength()

    def get_non_machine_id(self, index: int, non_machine_index: int) -> int:
        return self.data.Objects(index).NonMachines(non_machine_index).Id()

    def get_num_lights(self, index: int) -> int:
        return self.data.Objects(index).LightsLength()

    def get_light_id(self, index: int, light_index: int) -> int:
        return self.data.Objects(index).Lights(light_index).Id()

    def get_num_hinges(self, index: int) -> int:
        return self.data.Objects(index).HingesLength()

    def get_hinge_id(self, index: int, hinge_index: int) -> int:
        return self.data.Objects(index).Hinges(hinge_index).Id()

    def get_hinge_has_limits(self, index: int, hinge_index: int) -> bool:
        return self.data.Objects(index).Hinges(hinge_index).HasLimits()

    def get_hinge_min_limit(self, index: int, hinge_index: int) -> float:
        return self.data.Objects(index).Hinges(hinge_index).MinLimit()

    def get_hinge_max_limit(self, index: int, hinge_index: int) -> float:
        return self.data.Objects(index).Hinges(hinge_index).MaxLimit()

    def get_hinge_axis(self, index: int, hinge_index: int) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Objects(index).Hinges(hinge_index).Axis())

    def get_num_motors(self, index: int) -> int:
        return self.data.Objects(index).MotorsLength()

    def get_motor_id(self, index: int, motor_index: int) -> int:
        return self.data.Objects(index).Motors(motor_index).Id()

    def get_motor_has_limits(self, index: int, hinge_index: int) -> bool:
        return self.data.Objects(index).Motors(hinge_index).HasLimits()

    def get_motor_min_limit(self, index: int, hinge_index: int) -> float:
        return self.data.Objects(index).Motors(hinge_index).MinLimit()

    def get_motor_max_limit(self, index: int, hinge_index: int) -> float:
        return self.data.Objects(index).Motors(hinge_index).MaxLimit()

    def get_motor_axis(self, index: int, hinge_index: int) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Objects(index).Motors(hinge_index).Axis())

    def get_motor_force(self, index: int, motor_index: int) -> float:
        return self.data.Objects(index).Motors(motor_index).Force()

    def get_num_springs(self, index: int) -> int:
        return self.data.Objects(index).SpringsLength()

    def get_spring_id(self, index: int, spring_index: int) -> int:
        return self.data.Objects(index).Springs(spring_index).Id()

    def get_spring_has_limits(self, index: int, hinge_index: int) -> bool:
        return self.data.Objects(index).Springs(hinge_index).HasLimits()

    def get_spring_min_limit(self, index: int, hinge_index: int) -> float:
        return self.data.Objects(index).Springs(hinge_index).MinLimit()

    def get_spring_max_limit(self, index: int, hinge_index: int) -> float:
        return self.data.Objects(index).Springs(hinge_index).MaxLimit()

    def get_spring_axis(self, index: int, hinge_index: int) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Objects(index).Springs(hinge_index).Axis())

    def get_spring_force(self, index: int, spring_index: int) -> float:
        return self.data.Objects(index).Springs(spring_index).Force()

    def get_spring_damper(self, index: int, spring_index: int) -> float:
        return self.data.Objects(index).Springs(spring_index).Damper()

    def get_num_prismatic_joints(self, index: int) -> int:
        return self.data.Objects(index).PrismaticJointsLength()

    def get_prismatic_joint_id(self, index: int, prismatic_joint_index: int) -> int:
        return self.data.Objects(index).PrismaticJoints(prismatic_joint_index).Id()

    def get_prismatic_joint_limit(self, index: int, prismatic_joint_index: int) -> float:
        return self.data.Objects(index).PrismaticJoints(prismatic_joint_index).Limit()

    def get_prismatic_joint_axis(self, index: int, prismatic_joint_index: int) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Objects(index).PrismaticJoints(prismatic_joint_index).Axis())


class DynamicCompositeObjects(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._hinge_ids = self.data.HingeIdsAsNumpy().reshape(-1, 2)
        self._hinges = self.data.HingesAsNumpy().reshape(-1, 2)
        self._light_ids = self.data.LightIdsAsNumpy().reshape(-1, 2)
        self._lights = self.data.LightsAsNumpy()

    def get_data(self) -> DynComp.DynamicCompositeObjects:
        return DynComp.DynamicCompositeObjects.GetRootAsDynamicCompositeObjects(self.bytes, 0)

    def get_num_hinges(self) -> int:
        return self._hinge_ids.shape[0]

    def get_hinge_parent_id(self, index: int) -> int:
        return int(self._hinge_ids[index][0])

    def get_hinge_id(self, index: int) -> int:
        return int(self._hinge_ids[index][1])

    def get_hinge_angle(self, index: int) -> float:
        return float(self._hinges[index][0])

    def get_hinge_velocity(self, index: int) -> float:
        return float(self._hinges[index][1])

    def get_num_lights(self) -> int:
        return self._light_ids.shape[0]

    def get_light_parent_id(self, index: int) -> int:
        return int(self._light_ids[index][0])

    def get_light_id(self, index: int) -> int:
        return int(self._light_ids[index][1])

    def get_light_is_on(self, index: int) -> bool:
        return bool(self._lights[index])


class ObiParticles(OutputData):
    def get_data(self) -> ObiP.ObiParticles:
        return ObiP.ObiParticles.GetRootAsObiParticles(self.bytes, 0)

    def get_num_solvers(self) -> int:
        return self.data.SolversLength()

    def get_positions(self, index: int) -> np.ndarray:
        return self.data.Solvers(index).PositionsAsNumpy()

    def get_velocities(self, index: int) -> np.ndarray:
        return self.data.Solvers(index).VelocitiesAsNumpy()

    def get_num_objects(self) -> int:
        return self.data.ActorsLength()

    def get_object_id(self, index: int) -> int:
        return self.data.Actors(index).Id()

    def get_solver_id(self, index: int) -> int:
        return self.data.Actors(index).SolverId()

    def get_count(self, index: int) -> int:
        return self.data.Actors(index).Count()

    def get_solver_indices(self, index: int) -> np.ndarray:
        return self.data.Actors(index).SolverIndicesAsNumpy()


class Mouse(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._buttons: np.ndarray = self.data.ButtonsAsNumpy().reshape(3, 3)

    def get_data(self) -> Mous.Mouse:
        return Mous.Mouse.GetRootAsMouse(self.bytes, 0)

    def get_position(self) -> np.ndarray:
        return self.data.PositionAsNumpy()

    def get_scroll_delta(self) -> np.ndarray:
        return self.data.ScrollDeltaAsNumpy()

    def get_is_left_button_pressed(self) -> bool:
        return self._buttons[0][0]

    def get_is_left_button_held(self) -> bool:
        return self._buttons[0][1]

    def get_is_left_button_released(self) -> bool:
        return self._buttons[0][2]

    def get_is_middle_button_pressed(self) -> bool:
        return self._buttons[1][0]

    def get_is_middle_button_held(self) -> bool:
        return self._buttons[1][1]

    def get_is_middle_button_released(self) -> bool:
        return self._buttons[1][2]

    def get_is_right_button_pressed(self) -> bool:
        return self._buttons[2][0]

    def get_is_right_button_held(self) -> bool:
        return self._buttons[2][1]

    def get_is_right_button_released(self) -> bool:
        return self._buttons[2][2]


class TransformMatrices(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._matrices = self.data.MatricesAsNumpy().reshape(-1, 4, 4)

    def get_data(self) -> TranMat.TransformMatrices:
        return TranMat.TransformMatrices.GetRootAsTransformMatrices(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return self._ids[index]

    def get_matrix(self, index: int) -> np.array:
        return self._matrices[index]


class AvatarTransformMatrices(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._avatar_matrices = self.data.AvatarMatricesAsNumpy().reshape(-1, 4, 4)
        self._sensor_container_matrices = self.data.SensorContainerMatricesAsNumpy().reshape(-1, 4, 4)

    def get_data(self) -> AvTranMat.AvatarTransformMatrices:
        return AvTranMat.AvatarTransformMatrices.GetRootAsAvatarTransformMatrices(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.AvatarIdsLength()

    def get_id(self, index: int) -> str:
        return self.data.AvatarIds(index).decode('utf-8')

    def get_avatar_matrix(self, index: int) -> np.array:
        return self._avatar_matrices[index]

    def get_sensor_matrix(self, index: int) -> np.array:
        return self._sensor_container_matrices[index]
        
class FieldOfView(OutputData):
    def get_data(self) -> Fov.FieldOfView:
        return Fov.FieldOfView.GetRootAsFieldOfView(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_fov(self) -> float:
        return self.data.Fov()

    def get_focal_length(self) -> float:
        return self.data.FocalLength()


class Replicants(OutputData):
    def __init__(self, b):
        super().__init__(b)
        num_body_parts: int = self.get_num_body_parts()
        q = self.data.IdsAsNumpy()
        self._ids: np.ndarray = self.data.IdsAsNumpy().reshape(-1, num_body_parts)
        self._positions: np.ndarray = self.data.PositionsAsNumpy().reshape(-1, num_body_parts, 3)
        self._rotations: np.ndarray = self.data.RotationsAsNumpy().reshape(-1, num_body_parts, 4)
        self._forwards: np.ndarray = self.data.ForwardsAsNumpy().reshape(-1, num_body_parts, 3)
        self._held: np.ndarray = self.data.HeldAsNumpy().reshape(-1, 2, 2)
        self._collision_ids: np.ndarray = self.data.CollisionIdsAsNumpy().reshape(-1, num_body_parts - 1, 10)
        self._is_collisions: np.ndarray = self.data.IsCollisionsAsNumpy().reshape(-1, num_body_parts - 1, 10)
        self._statuses: np.ndarray = self.data.StatusesAsNumpy()

    def get_data(self) -> Repl.Replicants:
        return Repl.Replicants.GetRootAsReplicants(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return int(self._ids[index][0])

    def get_position(self, index: int) -> np.ndarray:
        return self._positions[index][0]

    def get_forward(self, index: int) -> np.ndarray:
        return self._forwards[index][0]

    def get_rotation(self, index: int) -> np.ndarray:
        return self._rotations[index][0]

    def get_body_part_id(self, index: int, body_part_index: int) -> int:
        return int(self._ids[index][body_part_index + 1])

    def get_body_part_position(self, index: int, body_part_index: int) -> np.ndarray:
        return self._positions[index][body_part_index + 1]

    def get_body_part_rotation(self, index: int, body_part_index: int) -> np.ndarray:
        return self._rotations[index][body_part_index + 1]

    def get_body_part_forward(self, index: int, body_part_index: int) -> np.ndarray:
        return self._forwards[index][body_part_index + 1]

    def get_is_holding_left(self, index: int) -> bool:
        return self._held[index][0][0] == 1

    def get_held_left(self, index: int) -> int:
        return int(self._held[index][0][1])

    def get_is_holding_right(self, index: int) -> bool:
        return self._held[index][1][0] == 1

    def get_held_right(self, index: int) -> int:
        return int(self._held[index][1][1])

    def get_is_collision(self, index: int, body_part_index: int, collision_index: int) -> bool:
        return self._is_collisions[index][body_part_index][collision_index]

    def get_collision_id(self, index: int, body_part_index: int, collision_index: int) -> int:
        return int(self._collision_ids[index][body_part_index][collision_index])

    def get_status(self, index: int) -> ActionStatus:
        return ActionStatus(self._statuses[index])

    def get_num_body_parts(self) -> int:
        return int(self.data.NumBodyParts())


class LeapMotion(OutputData):
    _NUM_BONES_PER_HAND: int = 16

    def __init__(self, b):
        super().__init__(b)
        self._positions: np.ndarray = self.data.PositionsAsNumpy().reshape(2, LeapMotion._NUM_BONES_PER_HAND, 3)
        self._rotations: np.ndarray = self.data.RotationsAsNumpy().reshape(2, LeapMotion._NUM_BONES_PER_HAND, 4)
        self._forwards: np.ndarray = self.data.ForwardsAsNumpy().reshape(2, LeapMotion._NUM_BONES_PER_HAND, 3)
        self._collision_ids: np.ndarray = self.data.CollisionsIdsAsNumpy()
        self._max_num_collisions: int = self._collision_ids.shape[0] // (LeapMotion._NUM_BONES_PER_HAND * 2)
        self._collision_ids = self._collision_ids.reshape((2, LeapMotion._NUM_BONES_PER_HAND, self._max_num_collisions))
        self._is_collisions: np.ndarray = self.data.IsCollisionsAsNumpy().reshape((2, LeapMotion._NUM_BONES_PER_HAND, self._max_num_collisions))
        self._angles: np.ndarray = self.data.AnglesAsNumpy().reshape(2, 25)
        self._button_presses: np.ndarray = self.data.ButtonsAsNumpy()

    def get_data(self) -> Leap.LeapMotion:
        return Leap.LeapMotion.GetRootAsLeapMotion(self.bytes, 0)

    def get_num_collisions_per_bone(self) -> int:
        return self._max_num_collisions

    def get_position(self, index: int, bone_index: int) -> np.ndarray:
        return self._positions[index][bone_index]

    def get_rotation(self, index: int, bone_index: int) -> np.ndarray:
        return self._rotations[index][bone_index]

    def get_forward(self, index: int, bone_index: int) -> np.ndarray:
        return self._forwards[index][bone_index]

    def get_is_collision(self, index: int, bone_index: int, collision_index: int) -> bool:
        return bool(self._is_collisions[index][bone_index][collision_index])

    def get_collision_id(self, index: int, bone_index: int, collision_index: int) -> int:
        return int(self._collision_ids[index][bone_index][collision_index])

    def get_angles(self, index: int, start_bone_index: int, end_bone_index: int) -> np.ndarray:
        return np.rad2deg(self._angles[index][start_bone_index: end_bone_index])

    def get_is_button_pressed(self, index: int) -> bool:
        return bool(self._button_presses[index])


class ReplicantSegmentationColors(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids: np.ndarray = self.data.IdsAsNumpy()
        self._colors: np.ndarray = self.data.ColorsAsNumpy().reshape(-1, 3)

    def get_data(self) -> RepSepCo.ReplicantSegmentationColors:
        return RepSepCo.ReplicantSegmentationColors.GetRootAsReplicantSegmentationColors(self.bytes, 0)

    def get_num(self) -> int:
        return int(self._ids.shape[0])

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_segmentation_color(self, index: int) -> np.ndarray:
        return self._colors[index]


class Framerate(OutputData):
    def get_data(self) -> Frame.Framerate:
        return Frame.Framerate.GetRootAsFramerate(self.bytes, 0)

    def get_target_framerate(self) -> int:
        return int(self.data.TargetFramerate())

    def get_frame_dt(self) -> float:
        return float(self.data.FrameDt())

    def get_physics_timestep(self) -> float:
        return float(self.data.PhysicsTimeStep())


class OccupancyMap(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._shape: np.ndarray = self.data.ShapeAsNumpy()
        self._map: np.ndarray = self.data.MapAsNumpy().reshape(self._shape)
        self._positions: np.ndarray = self.data.PositionsAsNumpy().reshape(self._shape[0], self._shape[1], 2)

    def get_data(self) -> Occ.OccupancyMap:
        return Occ.OccupancyMap.GetRootAsOccupancyMap(self.bytes, 0)

    def get_shape(self) -> np.ndarray:
        return self._shape

    def get_map(self) -> np.ndarray:
        return self._map

    def get_positions(self) -> np.ndarray:
        return self._positions


class EulerAngles(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids = self.data.IdsAsNumpy()
        self._rotations = self.data.RotationsAsNumpy().reshape(-1, 3)

    def get_data(self) -> Eulers.EulerAngles:
        return Eulers.EulerAngles.GetRootAsEulerAngles(self.bytes, 0)

    def get_num(self) -> int:
        return len(self._ids)

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_rotation(self, index: int) -> np.ndarray:
        return self._rotations[index]


class Drones(OutputData):
    def __init__(self, b):
        super().__init__(b)
        self._ids: np.ndarray = self.data.IdsAsNumpy()
        self._raycast_hits: np.ndarray = self.data.RaycastHitsAsNumpy()
        self._raycasts: np.ndarray = self.data.RaycastsAsNumpy().reshape(-1, 3)
        self._motor_ons: np.ndarray = self.data.MotorOnAsNumpy()

    def get_data(self) -> Dro.Drones:
        return Dro.Drones.GetRootAsDrones(self.bytes, 0)

    def get_num(self) -> int:
        return int(self._ids.shape[0])

    def get_id(self, index: int) -> int:
        return int(self._ids[index])

    def get_raycast_hit(self, index: int) -> bool:
        return bool(self._raycast_hits[index])

    def get_raycast(self, index: int) -> np.ndarray:
        return self._raycasts[index]

    def get_motor_on(self, index: int) -> bool:
        return bool(self._motor_ons[index])
