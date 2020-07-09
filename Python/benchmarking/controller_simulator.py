from time import time
from tdw.controller import Controller


"""
This is a minimal controller to test network performance.
"""

if __name__ == "__main__":
    num_trials = 1000
    sizes = [1, 1000, 10000, 700000]
    c = Controller()
    for size in sizes:
        c.communicate({"$type": "send_junk", "length": size, "frequency": "always"})
        t0 = time()
        for i in range(num_trials):
            c.communicate({"$type": "do_nothing"})
        fps = (num_trials / (time() - t0))

        print(round(fps))
