from typing import Union
from json import dumps, loads
from tdw.webgl.dashboard.request import Request


class Session:
    """
    Metadata for an ongoing session.
    """

    def __init__(self, session_id: int, request: Request = Request.none, response: Request = Request.none, message: str = ""):
        """
        :param session_id: The ID of the session.
        :param request: The current request as a `Request` enum value. The WebGL Build will read this and set `message` accordingly.
        :param response: The most recent request that was responded to as a `Request` enum value. The data in `message` is for this type of request.
        :param message: A string message from the WebGL Build in response to a request.
        """

        """:field
        The ID of the session.
        """
        self.session_id: int = session_id
        """:field
        The current request as a `Request` enum value. The WebGL Build will read this and set `message` accordingly.
        """
        self.request: Request = request
        """:field
        The most recent request that was responded to as a `Request` enum value. The data in `message` is for this type of request.
        """
        self.response: Request = response
        """:field
        A string message from the WebGL Build in response to a request.
        """
        self.message: str = message

    def to_json(self) -> str:
        """
        :return: This session as a JSON string.
        """

        return dumps({"id": self.session_id,
                      "request": self.request.name,
                      "response": self.response.name,
                      "message": self.message})


def from_json(json: Union[str, bytes]) -> Session:
    """
    :param json: A JSON string or bytes.

    :return: A session.
    """

    data = loads(json)
    return Session(session_id=data["id"],
                   request=Request[data["request"]],
                   response=Request[data["response"]],
                   message=data["message"])
