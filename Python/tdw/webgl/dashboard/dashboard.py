from typing import Dict
from flask import Flask, request
from flask_cors import cross_origin
from tdw.webgl.dashboard.request import Request, REQUEST_NAMES
from tdw.webgl.dashboard.session import Session, from_json


app = Flask(__name__)


@app.route('/api/get_sessions', methods=['GET'])
def get_sessions():
    """
    :return: JSON strings of every session separated by new lines.
    """

    return '\n'.join([s.to_json() for s in dashboard.sessions.values()])


@app.route('/api/create', methods=['POST'])
def create():
    """
    Create a new session.

    :return: The ID of the new session.
    """

    return str(dashboard.create())


@app.route('/api/<int:session_id>', methods=['GET', 'POST'])
@cross_origin()
def session(session_id: int):
    """
    Get or set a session.

    :param session_id: The ID of the session. If this session doesn't exist, nothing happens.

    :return: On GET: the session as a JSON string.
    """

    if session_id not in dashboard.sessions:
        return f'Invalid session ID: {session_id}'
    # Set the session from a JSON string.
    elif request.method == 'POST':
        if request.data != b'':
            data = request.data
        else:
            data = request.form["data"]
        dashboard.sessions[session_id] = from_json(data)
        return 'ok'
    # Return the session as a JSON string.
    else:
        # This session was killed.
        if dashboard.sessions[session_id].response == Request.kill:
            del dashboard.sessions[session_id]
            return 'killed'
        # Get the JSON string.
        else:
            return dashboard.sessions[session_id].to_json()


@app.route('/api/<int:session_id>/<request_type>', methods=['POST'])
def set_request(session_id: int, request_type: str):
    """
    Set a session's request type.

    :param session_id: The ID of the session. If this session doesn't exist, nothing happens.
    :param request_type: The type of request. See: `tdw.webgl.dashboard.request.Request`

    :return: 'ok' if the post succeeded.
    """

    if session_id not in dashboard.sessions:
        return f'Invalid session ID: {session_id}'
    elif request_type not in REQUEST_NAMES:
        return f'Invalid request {request_type} for session {session_id}'
    else:
        if dashboard.sessions[session_id].request == Request.none:
            # Set the request.
            dashboard.sessions[session_id].request = Request[request_type]
            # Clear the response.
            dashboard.sessions[session_id].response = Request.none
            dashboard.sessions[session_id].message = ""
            return 'ok'
        else:
            return f'Cannot set request for {session_id} because there is an ongoing request'


class Dashboard:
    """
    The Dashboard is a collection of ongoing sessions.

    Run this script to start the Flask process. See above for Flask app routes.
    """

    def __init__(self):
        """
        (no arguments)
        """

        """:field
        The ongoing sessions.
        """
        self.sessions: Dict[int, Session] = dict()
        self._next_id: int = 0

    def create(self) -> int:
        """
        Create a new session.

        :return: The ID of the new session.
        """

        session_id: int = self._next_id
        self.sessions[session_id] = Session(session_id=session_id)
        self._next_id += 1
        return session_id


dashboard = Dashboard()


def run_dashboard():
    from argparse import ArgumentParser

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument('--port', type=int, default=1453, help='The Dashboard server port.')
    parser.add_argument('--external', action='store_true',
                        help='If included, the Dashboard will serve non-local clients.')
    args, unknown = parser.parse_known_args()
    # Run the app.
    app.run(debug=True, host='0.0.0.0' if args.external else '127.0.0.1', port=args.port)


if __name__ == '__main__':
    run_dashboard()
