from typing import Dict, Union, List, Optional
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.robot import Robot
from tdw.robot_data.joint_type import JointType
from tdw.tdw_utils import TDWUtils


class UR5(Robot):
    def __init__(self, robot_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None):
        super().__init__(name="ur5", robot_id=robot_id, position=position, rotation=rotation)
        self.chain: Optional[Chain] = None
        # self.chain = ikpy.chain.Chain.from_urdf_file(str(Path("ur5_robot.urdf")), base_elements=["base_link"])

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        if self.chain is None:
            # Set the IK chain.
            links = [OriginLink()]
            for joint_id in self.static.joints:
                if self.static.joints[joint_id].joint_type == JointType.fixed_joint:
                    continue
                links.append(URDFLink(name=self.static.joints[joint_id].name,
                                      translation_vector=self._convert_for_ik(self.dynamic.joints[joint_id].position),
                                      orientation=np.array([0, 0, 0]),
                                      rotation=np.array([0, 1, 0]),
                                      bounds=(np.deg2rad(self.static.joints[joint_id].drives["x"].limits[0]),
                                              np.deg2rad(self.static.joints[joint_id].drives["x"].limits[1]))))
            self.chain = Chain(links=links)

    def reach_for(self, target: Union[np.ndarray, Dict[str, float]]) -> None:
        if isinstance(target, dict):
            target = TDWUtils.vector3_to_array(target)
        print(len(self.chain.links))
        print(len(self._get_initial_angles()))
        angles = self.chain.inverse_kinematics(target_position=UR5._convert_for_ik(target),
                                               initial_position=self._get_initial_angles())
        print(angles)

        for angle, joint_id in zip(angles, self.static.joints):
            if self.static.joints[joint_id].joint_type == JointType.fixed_joint:
                continue
            self.commands.append({"$type": "set_revolute_target",
                                  "id": self.robot_id,
                                  "joint_id": joint_id,
                                  "target": angle})

    @staticmethod
    def _convert_for_ik(arr: np.ndarray) -> np.array:
        return np.array([arr[2], -arr[0], arr[1]])

    def _get_initial_angles(self) -> np.array:
        """
        :return: The angles of the arm in the current state.
        """

        initial_angles = []
        for joint_id in self.dynamic.joints:
            if self.static.joints[joint_id].joint_type == JointType.fixed_joint:
                initial_angles.append(0)
            initial_angles.extend(self.dynamic.joints[joint_id].angles)
        return np.radians(initial_angles)


c = Controller()
ur5 = UR5(robot_id=c.get_unique_id())
camera = ThirdPersonCamera(position={"x": 0.5, "y": 1, "z": 0.5},
                           look_at={"x": 0.3, "y": 0, "z": 0.3})
c.add_ons.extend([ur5, camera])
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "destroy_all_objects"},
               {"$type": "set_screen_size", "width": 800, "height": 800},
               {"$type": "set_target_framerate", "framerate": 100}])
while ur5.joints_are_moving():
    c.communicate([])
reach_for_target = np.array([0.3, 0.7, 0.5])
ur5.reach_for(target=reach_for_target)
while ur5.joints_are_moving():
    c.communicate([])
end_link_id = ur5.static.joint_ids_by_name["wrist_3_link"]
print(np.linalg.norm(ur5.dynamic.joints[end_link_id].position - reach_for_target))
c.communicate({"$type": "terminate"})
