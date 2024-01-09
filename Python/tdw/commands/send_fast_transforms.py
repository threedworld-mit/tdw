# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_fixed_length_object_data_command import SendFixedLengthObjectDataCommand
from typing import List


class SendFastTransforms(SendFixedLengthObjectDataCommand):
    """
    Send FastTransforms output data. This is slightly faster than SendTransforms, and FastTransforms compresses much better than Transforms. However, FastTransforms excludes some data (see output data documentation) and it is also harder to use. See: send_object_ids which serializes the object IDs in the same order as the data in FastTransforms.
    """

    def __init__(self, ids: List[int] = None, frequency: str = "once"):
        """
        :param ids: Send data for objects with these IDs. If this is empty, data for all objects will be sent.
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(ids=ids, frequency=frequency)
