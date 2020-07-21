import zmq
from secrets import token_bytes
from json import loads


"""
This script simulates a build.
When it receives a message, the simulated build will send back a message.
This message is approximately the same size as that sent by a real TDW build.
This script is meant to be used to benchmark optimal network performance.
"""


if __name__ == "__main__":
    context = zmq.Context()

    outputs = {1: token_bytes(1),
               1000: token_bytes(1000),
               10000: token_bytes(10000),
               700000: token_bytes(700000)
               }

    # Use this socket to receive messages from the server.
    sock = context.socket(zmq.REQ)
    sock.connect("tcp://localhost:1071")

    key = 1
    while True:
        sock.send_multipart([outputs[key]])
        resp = loads(sock.recv_multipart()[0])[0]
        if resp["$type"] == "send_junk":
            key = resp["length"]
