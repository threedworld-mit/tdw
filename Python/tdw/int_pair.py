class IntPair:
    """
    A pair of unordered hashable integers. Use this class for dictionary keys.

    ```python
    import numpy as np
    from tdw.int_pair import IntPair

    id_0 = 0
    pos_0 = np.array([0, 1, 0])
    id_1 = 1
    pos_1 = np.array([-2, 2.5, 0.8])
    # Start a dictionary of distances between objects.
    distances = {IntPair(id_0, id_1): np.linalg.norm(pos_0 - pos_1)}
    ```
    """

    def __init__(self, int1: int, int2: int):
        """
        :param int1: The first integer.
        :param int2: The second integer.
        """

        """:field
        The first integer.
        """
        self.int1 = int1
        """:field
        The second integer.
        """
        self.int2 = int2

    def __eq__(self, other):
        if not isinstance(other, IntPair):
            return False
        return (other.int1 == self.int1 and other.int2 == self.int2) or\
               (other.int1 == self.int2 and other.int2 == self.int1)

    def __hash__(self):
        if self.int1 > self.int2:
            return hash((self.int1, self.int2))
        else:
            return hash((self.int2, self.int1))

    def __str__(self):
        return f"({self.int1}, {self.int2})"
