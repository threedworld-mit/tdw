# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_type_command import ObjectTypeCommand


class AddFloorplanFloodBuoyancy(ObjectTypeCommand):
    """
    Make an object capable of floating in a floorplan-flooded room. This is meant to be used only with the FloorplanFlood add-on.
    """

    def __init__(self, id: int):
        """
        :param id: The unique object ID.
        """

        super().__init__(id=id)

