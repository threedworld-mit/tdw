from time import time
from typing import List, Union
from pathlib import Path
import numpy as np
from tdw.output_data import OutputData, LeapMotion, VRRig
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.replicant.arm import Arm


class LeapMotionPoseRecorder(AddOn):
    """
    Record the pose of one or more hands using Leap Motion hand tracking.

    A *pose* in this case is a record of the rotations of the palm(s) and finger bones. It is not a *gesture*, which would be a record of the rotations and positions changing over time.

    This add-on assumes that you've already added an [`OculusLeapMotion`](oculus_leap_motion.md) add-on.

    This add-on doesn't include controls for how to start or stop recording; they must be user-defined.
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self._recording: bool = False
        self._t0: float = 0
        self._time_to_capture: float = 0
        self._path: str = ""
        self._hands: List[Arm] = list()

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        if self._recording:
            # Get the time elapsed.
            dt = time() - self._t0
            # Enough time has elapsed that we should capture the gesture.
            if dt >= self._time_to_capture:
                # Stop recording.
                self._recording = False
                # Record the rotations.
                arr = np.zeros(shape=(2, 16, 4))
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    # Get the rotations of the palms.
                    if r_id == "vrri":
                        vr_rig = VRRig(resp[i])
                        for hand in self._hands:
                            arr[hand.value][-1] = vr_rig.get_left_hand_rotation()
                    # Get the rotations of the fingers.
                    elif r_id == "leap":
                        leap_motion = LeapMotion(resp[i])
                        for hand in self._hands:
                            arr[hand.value][:-1] = leap_motion._rotations[hand.value]
                # Save the array.
                np.save(self._path, arr)

    def record(self, path: Union[str, Path], time_to_capture: float, hands: List[Arm]) -> None:
        """
        Prepare to record a hand pose.

        After a number of seconds greater than or equal to `time_to_capture` has elapsed, the pose will be recorded as a numpy array.

        The shape of the numpy array is always `(2, 16, 4)`: 2 hands, (5 fingers * 3 bones per finger) + palm, (x, y, z, w) quaternion.

        :param path: The path to the output file.
        :param time_to_capture: Wait this many seconds before capturing the pose.
        :param hands: A list of hands as [`Arm`](../replicant/arm.md) values to capture.
        """

        if self._recording:
            return
        p = TDWUtils.get_path(path=path)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        self._path = TDWUtils.get_string_path(path=path)
        if self._path.endswith(".npy"):
            self._path = self._path[:-4]
        self._time_to_capture = time_to_capture
        self._t0 = time()
        self._recording = True
        # Make sure the order of the hands is always the same.
        self._hands = list(sorted(hands))
