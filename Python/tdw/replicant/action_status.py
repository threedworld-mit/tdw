from enum import Enum


class ActionStatus(Enum):
    """
    The status of the Replicant after doing an action.

    Usage:

    With a [`Replicant` agent](Replicant.md):

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.replicant import Replicant, ActionStatus

    m = Replicant(replicant_id=0, position={"x": 0.5, "y": 0, "z": -1})
    c = Controller()
    c.add_ons.append(m)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    m.move_by(1)
    print(m.action.status) # ActionStatus.ongoing
    while m.action.status == ActionStatus.ongoing:
        c.communicate([])
    print(m.action.status) # ActionStatus.success
    c.communicate({"$type": "terminate"})
    ```

    If the status description states that the Replicant _tried to_ do something and failed, it means that the Replicant moved for _n_ frames before giving up.

    If the status description states that the Replicant _didn't try_ to do something, it means that the action failed without advancing the simulation at all.

    """

    ongoing = 0  # The action is ongoing.
    failure = 1  # Generic failure code (useful for custom APIs).
    success = 2  # The action was successful.
    failed_to_move = 3  # Tried to move to a target position or object but failed.
    failed_to_turn = 4  # Tried to turn but failed to align with the target angle, position, or object.
    cannot_reach = 5  # Didn't try to reach for the target position because it can't.
    failed_to_reach = 6  # Tried to reach for the target but failed; the magnet isn't close to the target.
    failed_to_grasp = 7  # Tried to grasp the object and failed.
    not_holding = 8  # Didn't try to drop the object(s) because it isn't holding them.
    clamped_camera_rotation = 9  # Rotated the camera but at least one angle of rotation was clamped.
    failed_to_bend = 10  # Tried to bend its arm but failed to bend it all the way.
    collision = 11  # Tried to move or turn but failed because it collided with the environment (such as a wall) or a large object (mass > 30).
    detected_obstacle = 12  # Boxcast detected an obstacle in replicant's path.
    held_by_other = 13  # Didn't try to grasp a target object because another Replicant is already holding it.
    already_holding = 14  # Replicant is already hodling an object in the requested arm.
    still_dropping = 15  # The Replicant dropped an object but, after many `communicate()` calls, the object is still moving.
