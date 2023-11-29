# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.webgl.trial_adders.trial_adder import TrialAdder


class Insert(TrialAdder):
    """
    Insert new trials into the current list of trials at a given index.
    """

    def __init__(self, index: int):
        """
        :param index: Insert the new trials at this index. If the index is greater than the current list of trials, the new trials will be added at the end of the list.
        """

        super().__init__()
        """:field
        Insert the new trials at this index. If the index is greater than the current list of trials, the new trials will be added at the end of the list.
        """
        self.index: int = index
