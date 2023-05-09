from enum import Enum


class ActionStatus(Enum):
    """
    The status of the drone after doing an action.
    """

    ongoing = 0  # The action is ongoing.
    failure = 1  # Generic failure code (useful for custom APIs).
    success = 2  # The action was successful.
    cannot_reach = 3  # Didn't try to reach for the target position because it can't.
    failed_to_reach = 4  # Tried to reach for the target but failed; the magnet isn't close to the target.
    collision = 5  # Tried to move or turn but failed because it collided with something.
    detected_obstacle = 6  # Detected an obstacle in its path.
