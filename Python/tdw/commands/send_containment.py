# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_data_command import SendDataCommand


class SendContainment(SendDataCommand):
    """
    Send containment data using container shapes. See: <computeroutput>add_box_container</computeroutput>, <computeroutput>add_cylinder_container</computeroutput>, and <computeroutput>add_sphere_container</computeroutput>. Container shapes will check for overlaps with other objects.
    """

    def __init__(self, frequency: str = "once"):
        """
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(frequency=frequency)
