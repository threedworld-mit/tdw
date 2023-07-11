from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.wheelchair_replicant.wheelchair_replicant_static import WheelchairReplicantStatic
from tdw.wheelchair_replicant.wheelchair_replicant_dynamic import WheelchairReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency


class DoNothing(Action):
    """
    A minimal custom action.
    """

    def get_initialization_commands(self, resp: List[bytes],
                                    static: WheelchairReplicantStatic,
                                    dynamic: WheelchairReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        return commands

    def get_ongoing_commands(self, resp: List[bytes],
                             static: WheelchairReplicantStatic,
                             dynamic: WheelchairReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        return commands

    def get_end_commands(self, resp: List[bytes],
                         static: WheelchairReplicantStatic,
                         dynamic: WheelchairReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        return commands


if __name__ == "__main__":
    c = Controller()
    replicant = WheelchairReplicant()
    c.add_ons.append(replicant)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    replicant.action = DoNothing()
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])
    print(replicant.action.status)
    c.communicate({"$type": "terminate"})
