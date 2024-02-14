from typing import Optional


class Parameter:
    """
    A parameter of a method.
    """

    def __init__(self, name: str, description: str, parameter_type: str, default_value: Optional[str]):
        """
        :param name: The name of the parameter.
        :param description: A description of the parameter.
        :param parameter_type: The value type.
        :param default_value: The default value, if any.
        """

        """:field
        The name of the parameter.
        """
        self.name: str = name
        """:field
        A description of the parameter.
        """
        self.description: str = description
        """:field
        The value type.
        """
        self.parameter_type: str = parameter_type
        """:field
        The default value, if any.
        """
        self.default_value: Optional[str] = default_value
