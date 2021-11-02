from time import time
from tdw.controller import Controller


"""
This is a minimal controller to test network performance.
"""

if __name__ == "__main__":
    num_trials = 50000
    sizes = [1, 1000, 10000, 700000]
    c = Controller(launch_build=False, check_version=False)
    results = dict()
    for size in sizes:
        c.communicate({"$type": "send_junk", "length": size, "frequency": "always"})
        t0 = time()
        for i in range(num_trials):
            if i % 200 == 0:
                print('num_trials=%d' % i)
            c.communicate({"$type": "do_nothing"})
        results[size] = (num_trials / (time() - t0))
    c.communicate({"stop": True})
    c.socket.close()
    print("")
    for size in results:
        print(size, round(results[size]))
