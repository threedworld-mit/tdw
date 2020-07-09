from time import time
from tdw.controller import Controller


"""
This is a minimal controller to test network performance with the ReqTest application.
"""

if __name__ == "__main__":
    num_trials = 1000
    c = Controller()

    cmd = {"$type": "do_nothing"}

    c.communicate(cmd)

    t0 = time()
    for i in range(num_trials):
        c.communicate(cmd)
    fps = (num_trials / (time() - t0))

    print(round(fps))
