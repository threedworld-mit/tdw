from enum import Enum


class Arm(Enum):
    """
    An enum that defines the side that an arm is on.

    ```python
    from tdw.replicant import Arm

    for arm in Arm:
        print(arm) # Arm.left, Arm.right
    ```

    """

    left = 0  # The left arm.
    right = 1  # The right arm.
