# Benchmark

`from tdw.add_ons.benchmark import Benchmark`

Benchmark the FPS over a given number of frames.

```python
from tdw.controller import Controller
from tdw.add_ons.benchmark import Benchmark

c = Controller()
b = Benchmark(num_frames=2000)
c.modules.append(b)
while b.fps < 0:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `fps` The average frames per second.

***

## Functions

#### \_\_init\_\_

**`Benchmark(num_frames)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| num_frames |  int |  | The number of frames over which to benchmark. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

_Returns:_  A list of commands that will initialize this module.

#### on_communicate

**`self.on_communicate(resp)`**

This is called after commands are sent to the build and a response is received.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

##### previous_commands

**`self.previous_commands(commands)`**

Do something with the commands that were just sent to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that were just sent to the build. |



