class WindSource:
    """
    A source of wind: An invisible Obi fluid that can dynamically adjust its rotation, speed, etc.
    """

    def __init__(self, visible: bool = False):
        """
        :param visible: If True, the wind fluid will be visible. This can be useful for debugging.
        """

        self._transparency: float = 1 if visible else 0
        self._thickness_cutoff: float = 1 if visible else 100
        
