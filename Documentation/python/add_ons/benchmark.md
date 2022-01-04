# Benchmark

`from tdw.add_ons.benchmark import Benchmark`

Benchmark the frames per second (FPS) over a given number of frames.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `times` A list of time elapsed per `communicate()` call.

- `fps` The frames per second of the previous benchmark test.

***

## Functions

#### \_\_init\_\_

**`Benchmark()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### before_send

**`self.before_send()`**

Start bencharking each `communicate()` call and clear `self.times`.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### start

**`self.start()`**

Start bencharking each `communicate()` call and clear `self.times`.

#### stop

**`self.stop()`**

Stop benchmarking each `communicate()` call and set `self.fps`.

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |



