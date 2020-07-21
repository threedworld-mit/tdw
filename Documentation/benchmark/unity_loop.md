# Unity, ZMQ and speed

The main loop of Unity Engine in the build _innately slows down the build_. This is unavoidable. We need to wait for the main loop to update in order to utilize most of Unity Engine (e.g. image capture).

 To test the slowdown of Unity, we compare it to an analogous Python script and minimal C# application.

### `build_simulator.py`

`build_simulator.py` simulates the build's network pattern and uses the same network library (ZMQ), but doesn't emulate any Unity processes.

`build_simulator.py` is an accurate test of optimal speed using ZMQ.

### The build + `send_junk`

By using a minimal controller, a compiled build, and the `send_junk` command, we can compare the build's performance to `build_simulator.py`.

### ReqTest

ReqTest is a minimal C# application built in Unity. It has the same network code and pattern as the build and `build_simulator.py`. Unlike the build, ReqTest doesn't wait for Unity's `Update()` callback to send and receive messages. 

### Implications

- `build_simulator.py` vs. ReqTest informs us of the innate slowdown of a Unity application and/or NetMQ (the C# implementation of ZMQ).
- ReqTest vs. the build informs us of the innate slowdown caused by the Unity `Update()` callback.

### Results

| Output data size (bytes) | `build_simulator.py` FPS    | ReqTest FPS | Compiled build FPS      |
| ---------------- | --------------------------- | ----------------------- | ----------------------- |
| 1                | 3171  | 1034 | 934 |
| 1000             | 3511 | 1124 | 917 |
| 10000            | 2346 | 505 | 515 |
| 700000           | 123 | 252 | 153 |

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

##### With ReqTest

```bash
cd <root>/Python/benchmarking
python3 req_test_creator.py
```

```bash
cd <root>/Python/benchmarking
python3 req_test_controller.py
```

```bash
cd <root>/dist/TDW_vTEST/TDW_vTEST_Windows/UtilityApplications/ReqTest
./ReqTest --length <length>
```

##### With a compiled build

```bash
cd <root>/Python/benchmarking
python3 build_simulator.py
```

```bash
<run build>
```

