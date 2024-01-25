from json import dumps, loads
from tdw.webgl.dashboard.request import Request


class Session:
    def __init__(self, session_id: int, request: Request = Request.none, response: str = ""):
        self.session_id: int = session_id
        self.request: Request = request
        self.response: str = response

    def to_json(self) -> str:
        return dumps({"id": self.session_id, "request": self.request.name, "response": self.response})


def from_json(json: str) -> Session:
    data = loads(json)
    return Session(session_id=data["id"], request=Request[data["request"]], response=data["response"])
