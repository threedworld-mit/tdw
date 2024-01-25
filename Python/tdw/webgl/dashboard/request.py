from enum import Enum


class Request(Enum):
    none = 0
    kill = 1
    get_trial_name = 2
    get_status = 3
    get_start_time = 4
    get_trial_start_time = 5
    get_trial_end_time = 6
    get_output_data = 7
