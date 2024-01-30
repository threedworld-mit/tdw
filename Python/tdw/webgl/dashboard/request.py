from typing import List
from enum import Enum


class Request(Enum):
    """
    Dashboard API calls.
    """

    none = 0  # No-op. This tells the WebGL build to listen again for an API request.
    kill = 1  # Stop the session.
    get_trial_name = 2  # Get the name of the ongoing trial or an empty string if there isn't one.
    get_status = 3  # Get the TrialStatus of the ongoing trial or an empty string if there isn't one.
    get_start_time = 4  # Get the time at which the session started as a string. To convert to a datetime, see: `Session.get_datetime()`.
    get_trial_start_time = 5  # Get the time at which an ongoing started as a string. Ignore this if there is no ongoing trial. To convert to a datetime, see: `Session.get_datetime()`.
    get_trial_end_time = 6  # Get the time at which the trial ended. Ignore this if the trial is ongoing. To convert to a datetime, see: `Session.get_datetime()`.
    get_output_data = 7  # Get the most recent frame's output data that the Build stored internally. To convert to a list of output data byte arrays, see: `Session.get_output_data()`.


REQUEST_NAMES: List[str] = [r.name for r in Request]
