from tdw.FBOutput import Vector3, Quaternion, PassMask, Color, MessageType, MachineType, SimpleTransform, PathState
from tdw.FBOutput import Environments as Envs
from tdw.FBOutput import Transforms as Trans
from tdw.FBOutput import Rigidbodies as Rigis
from tdw.FBOutput import Bounds as Bouns
from tdw.FBOutput import Images as Imags
from tdw.FBOutput import AvatarKinematic as AvKi
from tdw.FBOutput import AvatarNonKinematic as AvNoKi
from tdw.FBOutput import AvatarSimpleBody as AvSi
from tdw.FBOutput import AvatarStickyMitten as AvSM
from tdw.FBOutput import SegmentationColors as Segs
from tdw.FBOutput import AvatarSegmentationColor as AvSC
from tdw.FBOutput import AvatarStickyMittenSegmentationColors as AvSMSC
from tdw.FBOutput import IsOnNavMesh as IsNM
from tdw.FBOutput import IdPassGrayscale as IdGS
from tdw.FBOutput import Collision as Col
from tdw.FBOutput import ImageSensors as ImSe
from tdw.FBOutput import CameraMatrices as CaMa
from tdw.FBOutput import IdPassSegmentationColors as IdSC
from tdw.FBOutput import ArrivedAtNavMeshDestination as Arri
from tdw.FBOutput import FlexParticles as Flex
from tdw.FBOutput import VRRig as VR
from tdw.FBOutput import LogMessage as Log
from tdw.FBOutput import CompositeObjects as Comp
from tdw.FBOutput import Meshes as Me
from tdw.FBOutput import Substructure as Sub
from tdw.FBOutput import Version as Ver
from tdw.FBOutput import EnvironmentCollision as EnvCol
from tdw.FBOutput import Volumes as Vol
from tdw.FBOutput import AudioSources as Audi
from tdw.FBOutput import Raycast as Ray
from tdw.FBOutput import Overlap as Over
from tdw.FBOutput import NavMeshPath as Path
from tdw.FBOutput import StaticRobot as StRobo
from tdw.FBOutput import Robot as Robo
from tdw.FBOutput import Keyboard as Key
from tdw.FBOutput import Magnebot as Mag
from tdw.FBOutput import ScreenPosition as Screen
from tdw.FBOutput import TriggerCollision as Trigger
from tdw.FBOutput import LocalTransforms as LocalTran
from tdw.FBOutput import DriveAxis, JointType
from tdw.FBOutput import QuitSignal as QuitSig
import numpy as np
from typing import Tuple, Optional


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


class Environments(OutputData):
    def get_data(self) -> Envs.Environments:
        return Envs.Environments.GetRootAsEnvironments(self.bytes, 0)

    def get_center(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Envs(index).Center)

    def get_bounds(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Envs(index).Bounds)

    def get_id(self, index: int) -> int:
        return self.data.Envs(index).Id()

    def get_num(self) -> int:
        return self.data.EnvsLength()


class Transforms(OutputData):
    def get_data(self) -> Trans.Transforms:
        return Trans.Transforms.GetRootAsTransforms(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_position(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Position)

    def get_forward(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Forward)

    def get_rotation(self, index: int) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self.data.Objects(index).Rotation)


class Rigidbodies(OutputData):
    def get_data(self) -> Rigis.Rigidbodies:
        return Rigis.Rigidbodies.GetRootAsRigidbodies(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_velocity(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Velocity)

    def get_angular_velocity(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).AngularVelocity)

    def get_mass(self, index: int) -> float:
        return self.data.Objects(index).Mass()

    def get_sleeping(self, index: int) -> bool:
        return self.data.Objects(index).Sleeping()


class Bounds(OutputData):
    def get_data(self) -> Bouns.Bounds:
        return Bouns.Bounds.GetRootAsBounds(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_front(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Front)

    def get_back(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Back)

    def get_left(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Left)

    def get_right(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Right)

    def get_top(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Top)

    def get_bottom(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Bottom)

    def get_center(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Center)


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

    def get_image(self, index: int) -> np.array:
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


class AvatarStickyMitten(AvatarNonKinematic):
    def get_data(self) -> AvSM.AvatarStickyMitten:
        return AvSM.AvatarStickyMitten.GetRootAsAvatarStickyMitten(self.bytes, 0)

    def get_num_body_parts(self) -> int:
        return self.data.BodyPartsLength()

    def get_num_rigidbody_parts(self) -> int:
        return self.data.RigidbodyPartsLength()

    def get_body_part_position(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.BodyParts(index).Position)

    def get_body_part_rotation(self, index: int) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self.data.BodyParts(index).Rotation)

    def get_body_part_forward(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.BodyParts(index).Forward)

    def get_body_part_id(self, index: int) -> int:
        return self.data.BodyParts(index).Id()

    def get_rigidbody_part_velocity(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.RigidbodyParts(index).Velocity)

    def get_rigidbody_part_angular_velocity(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.RigidbodyParts(index).AngularVelocity)

    def get_rigidbody_part_mass(self, index: int) -> float:
        return self.data.RigidbodyParts(index).Mass()

    def get_rigidbody_part_sleeping(self, index: int) -> bool:
        return self.data.RigidbodyParts(index).Sleeping()

    def get_rigidbody_part_id(self, index: int) -> int:
        return self.data.RigidbodyParts(index).Id()

    def get_held_left(self) -> np.array:
        return self.data.HeldLeftAsNumpy()

    def get_held_right(self) -> np.array:
        return self.data.HeldRightAsNumpy()

    def get_angles_left(self) -> np.array:
        return self.data.AnglesLeftAsNumpy()

    def get_angles_right(self) -> np.array:
        return self.data.AnglesRightAsNumpy()

    def get_mitten_center_left_position(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.MittenCenterLeft().Position)

    def get_mitten_center_left_forward(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.MittenCenterLeft().Forward)

    def get_mitten_center_left_rotation(self) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self.data.MittenCenterLeft().Rotation)

    def get_mitten_center_right_position(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.MittenCenterRight().Position)

    def get_mitten_center_right_forward(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.MittenCenterRight().Forward)

    def get_mitten_center_right_rotation(self, index: int) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self.data.MittenCenterRight(index).Rotation)


class SegmentationColors(OutputData):
    def get_data(self) -> Segs.SegmentationColors:
        return Segs.SegmentationColors.GetRootAsSegmentationColors(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_object_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.Objects(index).SegmentationColor())

    def get_object_name(self, index: int) -> str:
        return self.data.Objects(index).Name().decode('utf-8')


class AvatarSegmentationColor(OutputData):
    def get_data(self) -> AvSC.AvatarSegmentationColor:
        return AvSC.AvatarSegmentationColor.GetRootAsAvatarSegmentationColor(self.bytes, 0)

    def get_id(self) -> str:
        return self.data.Id().decode('utf-8')

    def get_segmentation_color(self) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.SegmentationColor())


class AvatarStickyMittenSegmentationColors(OutputData):
    def get_data(self) -> AvSMSC.AvatarStickyMittenSegmentationColors:
        return AvSMSC.AvatarStickyMittenSegmentationColors.GetRootAsAvatarStickyMittenSegmentationColors(self.bytes, 0)

    def get_id(self) -> str:
        return self.data.Id().decode('utf-8')

    def get_num_body_parts(self) -> int:
        return self.data.BodyPartsLength()

    def get_body_part_id(self, index: int) -> int:
        return self.data.BodyParts(index).Id()

    def get_body_part_segmentation_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.BodyParts(index).SegmentationColor())

    def get_body_part_name(self, index: int) -> str:
        return self.data.BodyParts(index).Name().decode('utf-8')


class IsOnNavMesh(OutputData):
    def get_data(self) -> IsNM.IsOnNavMesh:
        return IsNM.IsOnNavMesh.GetRootAsIsOnNavMesh(self.bytes, 0)

    def get_position(self) -> Tuple[float, float, float]:
        return OutputData._get_xyz(self.data.Position())

    def get_is_on(self) -> bool:
        return self.data.IsOn()


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


class CameraMatrices(OutputData):
    def get_data(self) -> CaMa.CameraMatrices:
        return CaMa.CameraMatrices.GetRootAsCameraMatrices(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_projection_matrix(self) -> np.array:
        return self.data.ProjectionMatrixAsNumpy()

    def get_camera_matrix(self) -> np.array:
        return self.data.CameraMatrixAsNumpy()


class IdPassSegmentationColors(OutputData):
    def get_data(self) -> IdSC.IdPassSegmentationColors:
        return IdSC.IdPassSegmentationColors.GetRootAsIdPassSegmentationColors(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')

    def get_sensor_name(self) -> str:
        return self.data.SensorName().decode('utf-8')

    def get_num_segmentation_colors(self) -> int:
        return self.data.SegmentationColorsLength()

    def get_segmentation_color(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_rgb(self.data.SegmentationColors(index))


class ArrivedAtNavMeshDestination(OutputData):
    def get_data(self) -> Arri.ArrivedAtNavMeshDestination:
        return Arri.ArrivedAtNavMeshDestination.GetRootAsArrivedAtNavMeshDestination(self.bytes, 0)

    def get_avatar_id(self) -> str:
        return self.data.AvatarId().decode('utf-8')


class FlexParticles(OutputData):
    def get_data(self) -> Flex.FlexParticles:
        return Flex.FlexParticles.GetRootAsFlexParticles(self.bytes, 0)

    def get_num_objects(self) -> int:
        return self.data.ObjectsLength()

    def get_particles(self, index: int) -> np.array:
        return self.data.Objects(index).ParticlesAsNumpy().view(dtype=np.float32).reshape(-1, 4)

    def get_velocities(self, index: int) -> np.array:
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


class CompositeObjects(OutputData):
    MACHINE_TYPES = {MachineType.MachineType.light: "light",
                     MachineType.MachineType.motor: "motor",
                     MachineType.MachineType.hinge: "hinge",
                     MachineType.MachineType.spring: "spring",
                     MachineType.MachineType.none: "none"}

    def get_data(self) -> Comp.CompositeObjects:
        return Comp.CompositeObjects.GetRootAsCompositeObjects(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_num_sub_objects(self, index: int) -> int:
        return self.data.Objects(index).SubObjectsLength()

    def get_sub_object_id(self, index: int, sub_object_index: int) -> int:
        return self.data.Objects(index).SubObjects(sub_object_index).Id()

    def get_sub_object_machine_type(self, index: int, sub_object_index: int) -> str:
        return CompositeObjects.MACHINE_TYPES[self.data.Objects(index).SubObjects(sub_object_index).MachineType()]


class Meshes(OutputData):
    def get_data(self) -> Me.Meshes:
        return Me.Meshes.GetRootAsMeshes(self.bytes, 0)

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_vertices(self, index: int) -> np.array:
        return self.data.Objects(index).VerticesAsNumpy().view(dtype=np.float32).reshape(-1, 3)

    def get_triangles(self, index: int) -> np.array:
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
    def get_data(self) -> Vol.Volumes:
        return Vol.Volumes.GetRootAsVolumes(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_volume(self, index: int) -> float:
        return self.data.Objects(index).Volume()


class AudioSources(OutputData):
    def get_data(self) -> Audi.AudioSources:
        return Audi.AudioSources.GetRootAsAudioSources(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_object_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_is_playing(self, index: int) -> bool:
        return self.data.Objects(index).IsPlaying()


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

    def get_object_ids(self) -> np.array:
        return self.data.ObjectIdsAsNumpy()

    def get_env(self) -> bool:
        return self.data.Env()


class NavMeshPath(OutputData):
    _STATES = {PathState.PathState.complete: "complete",
               PathState.PathState.invalid: "invalid",
               PathState.PathState.partial: "partial"}

    def get_data(self) -> Path.NavMeshPath:
        return Path.NavMeshPath.GetRootAsNavMeshPath(self.bytes, 0)

    def get_state(self) -> str:
        return NavMeshPath._STATES[self.data.State()]

    def get_path(self) -> np.array:
        return self.data.PathAsNumpy().view(dtype=np.float32).reshape(-1, 3)

    def get_id(self) -> int:
        return self.data.Id()


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


class Robot(OutputData):
    def get_data(self) -> Robo.Robot:
        return Robo.Robot.GetRootAsRobot(self.bytes, 0)
    
    def get_id(self) -> int:
        return self.data.Id()

    def get_position(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Transform().Position)

    def get_rotation(self) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self.data.Transform().Rotation)

    def get_forward(self) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Transform().Forward)

    def get_num_joints(self) -> int:
        return self.data.JointsLength()

    def get_joint_id(self, index: int) -> int:
        return self.data.Joints(index).Id()

    def get_joint_position(self, index: int) -> np.array:
        return self.data.Joints(index).PositionAsNumpy()

    def get_joint_positions(self, index: int) -> np.array:
        return np.degrees(self.data.Joints(index).PositionsAsNumpy())

    def get_immovable(self) -> bool:
        return self.data.Immovable()


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

    def get_held_left(self) -> np.array:
        return self.data.HeldLeftAsNumpy()

    def get_held_right(self) -> np.array:
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
    def get_data(self) -> LocalTran.LocalTransforms:
        return LocalTran.LocalTransforms.GetRootAsLocalTransforms(self.bytes, 0)

    def get_num(self) -> int:
        return self.data.ObjectsLength()

    def get_id(self, index: int) -> int:
        return self.data.Objects(index).Id()

    def get_position(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Position)

    def get_forward(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Forward)

    def get_eulers(self, index: int) -> Tuple[float, float, float]:
        return OutputData._get_vector3(self.data.Objects(index).Eulers)

    def get_rotation(self, index: int) -> Tuple[float, float, float, float]:
        return OutputData._get_quaternion(self.data.Objects(index).Rotation)


class QuitSignal(OutputData):
    def get_data(self) -> QuitSig.QuitSignal:
        return QuitSig.QuitSignal.GetRootAsQuitSignal(self.bytes, 0)

    def get_ok(self) -> bool:
        return self.data.Ok()
