from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Dict
from tdw.add_ons.agent.agent import Agent
from tdw.add_ons.agent.robot.robot_static import RobotStatic
from tdw.add_ons.agent.robot.robot_dynamic import RobotDynamic

T = TypeVar("T", bound=RobotStatic)
U = TypeVar("U", bound=RobotDynamic)


class RobotBase(Generic[T, U], Agent[int, T, U], ABC):
    """
    Abstract base class for robot agents.
    """

    def __init__(self, agent_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None):
        """
        :param agent_id: The ID of the robot.
        :param position: The position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the robot in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        """

        super().__init__(agent_id=agent_id)

        if position is None:
            self._initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            self._initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self._initial_rotation: Dict[str, float] = rotation

        self._add_robot_command: dict = self._get_add_robot_command()

    def get_initialization_commands(self) -> List[dict]:
        return [self._add_robot_command,
                {"$type": "send_static_robots",
                 "frequency": "once"},
                {"$type": "send_robots",
                 "frequency": "always"}]

    @abstractmethod
    def _get_add_robot_command(self) -> dict:
        """
        :return: A command to add the robot.
        """

        raise Exception()
