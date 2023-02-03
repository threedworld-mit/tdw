from enum import Enum


class ActionStatus(Enum):
    """
    The status of the Replicant after doing an action.
    """

    ongoing = 0  # The action is ongoing.
    failure = 1  # Generic failure code (useful for custom APIs).
    success = 2  # The action was successful.
    failed_to_move = 3  # Tried to move to a target position or object but failed.
    failed_to_turn = 4  # Tried to turn but failed to align with the target angle, position, or object.
    cannot_reach = 5  # Didn't try to reach for the target position because it can't.
    failed_to_reach = 6  # Tried to reach for the target but failed; the magnet isn't close to the target.
    not_holding = 7  # Didn't try to drop the object(s) because it isn't holding them.
    collision = 8  # Tried to move or turn but failed because it collided with something.
    detected_obstacle = 9  # Detected an obstacle in its path.
    already_holding = 10  # Already holding the object.
    still_dropping = 11  # Dropped an object but, after many `communicate()` calls, the object is still moving.
    cannot_grasp = 12  # Didn't try to grasp the object because it's of an invalid type (e.g. a kinematic object).
