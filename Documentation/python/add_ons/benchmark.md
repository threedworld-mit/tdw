# Benchmark

`from tdw.add_ons.benchmark import Benchmark`

Benchmark the frames per second (FPS) over a given number of frames.

***

## Fields

- `times` A list of time elapsed per `communicate()` call.

- `fps` The frames per second of the previous benchmark test.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Benchmark()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

Update the time.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### start

**`self.start()`**

Start benchmarking each `communicate()` call and clear `self.times`.

#### stop

**`self.stop()`**

Stop benchmarking each `communicate()` call and set `self.fps`.