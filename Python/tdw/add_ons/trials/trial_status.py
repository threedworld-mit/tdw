from enum import Enum


class TrialStatus(Enum):
    uninitialized = 0
    running = 1
    success = 2
    failure = 3
