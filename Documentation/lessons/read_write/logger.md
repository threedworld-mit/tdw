##### Read/Write to Disk

# The `Logger` and `LogPlayback` add-ons

## 1. `Logger`

The [`Logger`](../../python/add_ons/logger.md) add-on will log every command sent to the build to a text file per `communicate()` call. It can later read that text file and send those commands to the build. The `Logger` can be very useful when debugging code.

Add a `Logger` just like you'd add any other add-on:

```python
from tdw.controller import Controller
from tdw.add_ons.logger import Logger

c = Controller()
logger = Logger(path="log.txt")
c.add_ons.append(logger)
# The logger add-on will log this command.
c.communicate({"$type": "do_nothing"})
# The logger add-on will log this command and generate a log.txt file.
c.communicate({"$type": "terminate"})
```

- `path` is the path to the log file. It can be a string or a [`Path`](https://docs.python.org/3/library/pathlib.html).
- Optionally, you can set `overwrite=True` in the constructor. If `True`, and if a log file already exists at `path`, the log file will be overwritten.
- Optionally, you can set `log_commands_in_build=True` in the constructor. This will log each list of commands in the [Player log](https://docs.unity3d.com/Manual/LogFiles.html).

This controller will add three random objects to the scene and log the commands:

```python
import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.logger import Logger

c = Controller()
logger = Logger(path="log.txt")
c.add_ons.append(logger)

commands = [TDWUtils.create_empty_room(12, 12)]
models = ["iron_box", "rh10", "basket_18inx18inx12iin_bamboo", "vase_02"]
x = -2
for i in range(3):
    model_name: str = random.choice(models)
    commands.append(c.get_add_object(model_name=model_name,
                                     object_id=c.get_unique_id(),
                                     position={"x": x, "y": 0, "z": 0}))
    x += 1
c.communicate(commands)
c.communicate({"$type": "terminate"})
```

## 2. `LogPlayback`

The [`LogPlayback`](../../python/add_ons/log_playback.md) add-on can read a log file of commands and re-send the commands. Combined with `Logger`, this will let you re-create scenes by playing back exact sequences of lists of commands:

```python
from tdw.controller import Controller
from tdw.add_ons.log_playback import LogPlayback

c = Controller()
log_playback = LogPlayback()
c.add_ons.append(log_playback)
# Load the commands.
log_playback.load(path="log.txt")
# Play back each list of commands.
while len(log_playback.playback) > 0:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Note that we are calling `c.communicate([])`, supplying an empty list. You shouldn't add the playback's commands to this list or else they'll be sent twice. This is because `log_playback` automatically appends the next list of commands within the `communicate()` call (just like any other add-on).

***

**Next: [The `JsonWriter` add-on](json.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`Logger`](../../python/add_ons/logger.md)
- [`LogPlayback`](../../python/add_ons/log_playback.md)