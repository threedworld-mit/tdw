from time import sleep
from threading import Thread
from typing import Callable
from datetime import datetime
from requests import post, get, ConnectTimeout
from tdw.output_data import OutputData, FastTransforms
from tdw.webgl import TrialController, TrialMessage, TrialPlayback, END_MESSAGE, run
from tdw.webgl.trial_adders import AtEnd
from tdw.webgl.trials.tests.dashboard_test import DashboardTest
from tdw.webgl.dashboard import Request, Session, from_json


base_url = 'http://127.0.0.1:1453'


def do_post(request: Request) -> None:
    """
    Send an HTTP post to the Dashboard.

    :param request: The request type.
    """

    resp = post(f'{base_url}/0/{request.name}')
    assert resp.status_code == 200, resp.status_code
    assert resp.text == 'ok', resp.text


def send(request: Request, expected_message: str, assertion: Callable[[Session, str], bool]) -> None:
    """
    Send an HTTP post and await a response.

    :param request: The request type.
    :param expected_message: The expected message. This is only used in equality checks.
    :param assertion: A fucntion that asserts that the session message is an expected value.
    """

    do_post(request)
    got_response = False
    url = f'{base_url}/0'
    for i in range(60):
        try:
            resp = get(url, timeout=1)
            assert resp.status_code == 200, resp.status_code
            session = from_json(resp.text)
            if session.response != Request.none:
                assert assertion(session, expected_message), session.message
                got_response = True
                break
            sleep(1)
        except ConnectTimeout:
            pass
    if not got_response:
        raise Exception("Failed to get a response from the build")


def assert_equality(session: Session, expected_message: str) -> bool:
    """
    :param session: The session.
    :param expected_message: The expected message.

    :return: True if the session's message is equal to the expected message.
    """

    return session.message == expected_message


def assert_datetime(session: Session, _: str) -> bool:
    """
    :param session: The session.
    :param _: Not used.

    :return: True if session.message is a valid datetime string.
    """

    try:
        datetime.strptime(session.message, '%m/%d/%Y %H:%M:%S')
        return True
    except TypeError:
        return False


def assert_output_data(session: Session, _: str) -> bool:
    """
    :param session: The session.
    :param _: Not used.

    :return: True if session.message is output data containing transforms data with a position of approximately (0, 0, 0).
    """

    resp = session.get_output_data()
    assert len(resp) > 0, resp
    ftra = False
    for i in range(len(resp)):
        r_id = OutputData.get_data_type_id(resp[i])
        if r_id == "ftra":
            ftra = True
            position = [round(c, 2) for c in FastTransforms(resp[i]).get_position(0).tolist()]
            assert sum(position) == 0, position
    return ftra


def test_equality(request: Request, expected_message: str) -> None:
    """
    Test message equality.

    :param request: The request.
    :param expected_message: The message used for the quality check.
    :return:
    """
    send(request, expected_message, assert_equality)


def test_datetime(request: Request) -> None:
    """
    Datetime validation.

    :param request: The request.
    """

    send(request, "", assert_datetime)


def http_test():
    """
    Test each type of Dashboard request.
    """

    test_equality(Request.get_trial_name, "DashboardTest")
    test_equality(Request.get_status, "running")
    test_datetime(Request.get_start_time)
    test_datetime(Request.get_trial_start_time)
    test_datetime(Request.get_trial_end_time)
    send(Request.get_output_data, "", assert_output_data)
    # Kill the session.
    post(f'{base_url}/0/kill')


class DashboardTrialController(TrialController):
    """
    A TrialController that can be used to test the Dashboard.

    This will spawn a thread that will start making Dashboard API calls.
    """

    def get_initial_message(self) -> TrialMessage:
        # Tell the Dashboard that this session exists by "creating" it.
        resp = post(f'{base_url}/create')
        assert resp.status_code == 200, resp.status_code
        assert resp.text == '0', resp.text
        # Start the HTTP tests.
        t = Thread(target=http_test)
        t.start()
        # Send the trial.
        return TrialMessage(trials=[DashboardTest()], adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE


if __name__ == "__main__":
    d = DashboardTrialController()
    run(d, session_id=0)
