from typing import List


class LisdfRobotMetadata:
    """
    Metadata for how to add a robot from a .urdf file referenced by a .lisdf file.
    This will create a "fixed" version of a .urdf file that includes simplified namespaces, removed links, etc.
    """

    def __init__(self, name: str, link_name_excludes_regex: List[str] = None, link_exclude_types: List[str] = None):
        """
        :param name: The name of the robot.
        :param link_name_excludes_regex: A list of regular expressions to search for in links, for example `["_gazebo_"]`. Link names that match this will be removed.
        :param link_exclude_types: Some links have a `type` attribute. Exclude links matching this types in this list, for example `["laser", "camera"]`.
        """

        """:field
        The name of the robot.
        """
        self.name: str = name
        if link_name_excludes_regex is None:
            """:field
            A list of regular expressions to search for in links, for example `["_gazebo_"]`. Link names that match this will be removed.
            """
            self.link_name_excludes_regex: List[str] = list()
        else:
            self.link_name_excludes_regex = link_name_excludes_regex
        if link_exclude_types is None:
            """:field
            Some links have a `type` attribute. Exclude links matching this types in this list, for example `["laser", "camera"]`.
            """
            self.link_exclude_types: List[str] = list()
        else:
            self.link_exclude_types = link_exclude_types
