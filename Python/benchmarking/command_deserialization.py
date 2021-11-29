import json
from tdw.controller import Controller
from tdw.add_ons.benchmark import Benchmark


"""
Do nothing. Then, do a *lot* of nothing.

This script sends the do_nothing command once per frame for a thousand trials.
Then, it sends it twice per frame, then four times per frame, etc.

This will output the FPS per number of times do_nothing is sent per frame.

This way, it is possible to gauge the effect that Command deserialization has on overall speed.
"""

if __name__ == "__main__":
    c = Controller(launch_build=False)
    b = Benchmark()
    c.add_ons.append(b)
    c.communicate({"$type": "create_empty_environment"})
    cmd = {"$type": "do_nothing"}
    output = "| Quantity | Size (bytes) | FPS |\n| --- | --- | --- |\n"
    sizes = []
    for quant in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
        cmds = []
        for q in range(quant):
            cmds.append(cmd)
        size = len(json.dumps(cmds).encode('utf-8'))
        sizes.append(size)
        b.start()
        for trial in range(1000):
            c.communicate(cmds)
        b.stop()
        output += "| " + str(quant) + " | " + str(size) + " | " + str(round(b.fps)) + " |\n"
    print("")
    print(output)
    c.communicate({"$type": "terminate"})
