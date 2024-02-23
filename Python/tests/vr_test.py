from tdw.controller import Controller
from tdw.output_data import VRRig, OutputData
from tdw.tdw_utils import TDWUtils

"""
Test output data sent from a VR rig.
"""


class VRTest(Controller):
    """
    Test the output data sent from a VR rig.
    """

    def run(self):
        """
        1. Start TDW and load an empty room.
        2. Create the VR rig.
        3. Request VR data per frame.
        4. Continuously receive VR data. If the data is different from the previous state, print it to the console.
        """

        self.communicate(TDWUtils.create_empty_room(20, 20))

        self.communicate({"$type": "create_vr_rig",
                          "rig_type": "oculusLeap"})

        print("Created the VR Rig.")

        resp = self.communicate({"$type": "send_vr_rig",
                                 "frequency": "always"})

        # Get the initial VR state.
        vr_0 = self.get_vr_state(resp)

        # Start an infinite loop.
        while True:
            # Get new VR data.
            resp = self.communicate({"$type": "do_nothing"})
            vr_1 = self.get_vr_state(resp)

            # Compare the old VR data to the new. If there was an update, print to console.
            if not self.vr_states_are_equal(vr_0, vr_1):
                self.print_vr_data(vr_1)
            # Update the current VR state.
            vr_0 = vr_1

    @staticmethod
    def get_vr_state(resp) -> VRRig:
        """
        Get VRRig data from the byte array response.

        :param resp: The response.
        """

        assert len(resp) > 0, "No VR data received in response: " + str(resp)
        assert OutputData.get_data_type_id(resp[0]) == "vrri", resp[0]

        return VRRig(resp[0])

    @staticmethod
    def print_vr_data(vr: VRRig) -> None:
        """
        Print VR data to the console.

        :param vr: The VR data.
        """

        # Print the root object's data.
        print("Position:" + str(vr.get_position()))
        print("Rotation: " + str(vr.get_rotation()))
        print("Forward: " + str(vr.get_forward()))

        # Print the left hand's data.
        print("Left Hand:")
        print("\tPosition: " + str(vr.get_left_hand_position()))
        print("\tRotation: " + str(vr.get_left_hand_rotation()))
        print("\tForward: " + str(vr.get_left_hand_forward()))

        # Print the right hand's data.
        print("Right Hand:")
        print("\tPosition: " + str(vr.get_right_hand_position()))
        print("\tRotation: " + str(vr.get_right_hand_rotation()))
        print("\tForward: " + str(vr.get_right_hand_forward()))

        # Print the had.
        print("Head:")
        print("\tPosition: " + str(vr.get_head_position()))
        print("\tRotation: " + str(vr.get_head_rotation()))
        print("\tForward: " + str(vr.get_head_forward()))

        # Print an extra line.
        print("")

    @staticmethod
    def vr_states_are_equal(vr_0: VRRig, vr_1: VRRig) -> bool:
        """
        Compare to VRRig data objects for equality.

        :param vr_0: The original VR data.
        :param vr_1: The new VR data.
        """

        # Compare each tuple.
        for my_tup, their_tup in zip([vr_0.get_position(), vr_0.get_rotation(), vr_0.get_forward(),
                                      vr_0.get_left_hand_position(), vr_0.get_left_hand_rotation(),
                                      vr_0.get_left_hand_rotation(),
                                      vr_0.get_right_hand_position(), vr_0.get_right_hand_rotation(),
                                      vr_0.get_right_hand_forward(),
                                      vr_0.get_head_position(), vr_0.get_head_rotation(), vr_0.get_head_forward()],
                                     [vr_1.get_position(), vr_1.get_rotation(), vr_1.get_forward(),
                                      vr_1.get_left_hand_position(), vr_1.get_left_hand_rotation(),
                                      vr_1.get_left_hand_rotation(),
                                      vr_1.get_right_hand_position(), vr_1.get_right_hand_rotation(),
                                      vr_1.get_right_hand_forward(),
                                      vr_1.get_head_position(), vr_1.get_head_rotation(), vr_1.get_head_forward()]):

            # These lists are long and complicated; this naively checks if they are both in the same order.
            # If the lengths of the tuples are different, we're probably accidently comparing apples and oranges,
            # i.e. position to rotation.
            assert len(my_tup) == len(their_tup), "The lengths of these tuples are different: " + \
                                                  str(my_tup) + ", " + str(their_tup)

            for my_value, their_value in zip(my_tup, their_tup):
                # Test if the values are nearly equal.
                if abs(my_value - their_value) >= 0.01:
                    return False
        return True


if __name__ == "__main__":
    VRTest().run()
