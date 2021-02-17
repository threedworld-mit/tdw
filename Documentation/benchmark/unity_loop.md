# Unity, ZMQ and speed

The main loop of Unity Engine in the build _innately slows down the build_. This is unavoidable. We need to wait for the main loop to update in order to utilize most of Unity Engine (e.g. image capture).

 To test the slowdown of Unity, we compare it to an analogous Python script and minimal C# application.

### `build_simulator.py`

`build_simulator.py` simulates the build's network pattern and uses the same network library (ZMQ), but doesn't emulate any Unity processes.

`build_simulator.py` is an accurate test of optimal speed using ZMQ.

### The build + `send_junk`

By using a minimal controller, a compiled build, and the `send_junk` command, we can compare the build's performance to `build_simulator.py`.

### Results

| Output data size (bytes) | `build_simulator.py` FPS    |
| ---------------- | --------------------------- |
| 1                | 3171  |
| 1000             | 3511 |
| 10000            | 2346 |
| 700000           | 123 |

### How to run this test

##### With `build_simulator.py`

```bash
cd <root>/Python/benchmarking
python3 build_simulator.py
```

```bash
cd <root>/Python/benchmarking
python3 controller_simulator.py
```

