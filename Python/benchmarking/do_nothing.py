import json
from time import time
from tdw.controller import Controller


"""
Do nothing. Then, do a *lot* of nothing.

This script sends the do_nothing command once per frame for a thousand trials.
Then, it sends it twice per frame, then four times per frame, etc.

This will output the FPS per number of times do_nothing is sent per frame.

This way, it is possible to gauge the effect that Command deserialization has on overall speed.
"""

if __name__ == "__main__":
    c = Controller()

    c.start()
    c.communicate({"$type": "create_empty_environment"})

    quantities = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

    cmd = {"$type": "do_nothing"}

    num_trials = 1000

    output = "| Quantity | Size (bytes) | FPS |\n| --- | --- | --- |\n"

    sizes = []

    for quant in quantities:
        cmds = []
        for q in range(quant):
            cmds.append(cmd)

        size = len(json.dumps(cmds).encode('utf-8'))
        sizes.append(size)

        t0 = time()
        for trial in range(num_trials):
            c.communicate(cmds)
        fps = (num_trials / (time() - t0))
        output += "| " + str(quant) + " | " + str(size) + " | " + str(round(fps)) + " |\n"

    print("")
    print(output)
    c.communicate({"$type": "terminate"})
