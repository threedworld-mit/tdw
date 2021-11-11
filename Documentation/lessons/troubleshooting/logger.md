##### Troubleshooting

# The `Logger` add-on

The [`Logger`](../../python/add_ons/logger.md) add-on will log every command sent to the build to a text file. It can later read that text file and send those commands to the build. The `Logger` can be very useful when debugging code because it will allow you to capture and replay behavior without needing to use any particular controller.

Add a `Logger` just like you'd add any other add-on:

```python
from tdw.controller import Controller
from tdw.add_ons.logger import Logger

c = Controller()
logger = Logger(record=True, path="log.json")
c.add_ons.append(logger)
# The logger add-on will log this command.
c.communicate({"$type": "do_nothing"})
# The logger add-on will log this command and generate a log.json file.
c.communicate({"$type": "terminate"})
```

- If `record` is True, the `Logger` will record each list of commands sent to the build. If False, the `Logger` will try to read an existing log file and send those commands to the build per frame.
- `path` is the path to the log file. It can be a string or a [`Path`](https://docs.python.org/3/library/pathlib.html).
- Optionally, you can set `log_commands_in_build=True` in the constructor. This will log each list of commands in the [Player log](https://docs.unity3d.com/Manual/LogFiles.html).

## Log commands

This controller will add three random objects to the scene and log the commands. They will be stored in `log.json` as well as `logger.playback`:

```python
import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.logger import Logger

c = Controller()
logger = Logger(record=True, path="log.json")
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
for commands in logger.playback:
    print(commands)
```

Output:

```
[{'$type': 'create_exterior_walls', 'walls': [{'x': 0, 'y': 0}, {'x': 0, 'y': 1}, {'x': 0, 'y': 2}, {'x': 0, 'y': 3}, {'x': 0, 'y': 4}, {'x': 0, 'y': 5}, {'x': 0, 'y': 6}, {'x': 0, 'y': 7}, {'x': 0, 'y': 8}, {'x': 0, 'y': 9}, {'x': 0, 'y': 10}, {'x': 0, 'y': 11}, {'x': 1, 'y': 0}, {'x': 1, 'y': 11}, {'x': 2, 'y': 0}, {'x': 2, 'y': 11}, {'x': 3, 'y': 0}, {'x': 3, 'y': 11}, {'x': 4, 'y': 0}, {'x': 4, 'y': 11}, {'x': 5, 'y': 0}, {'x': 5, 'y': 11}, {'x': 6, 'y': 0}, {'x': 6, 'y': 11}, {'x': 7, 'y': 0}, {'x': 7, 'y': 11}, {'x': 8, 'y': 0}, {'x': 8, 'y': 11}, {'x': 9, 'y': 0}, {'x': 9, 'y': 11}, {'x': 10, 'y': 0}, {'x': 10, 'y': 11}, {'x': 11, 'y': 0}, {'x': 11, 'y': 1}, {'x': 11, 'y': 2}, {'x': 11, 'y': 3}, {'x': 11, 'y': 4}, {'x': 11, 'y': 5}, {'x': 11, 'y': 6}, {'x': 11, 'y': 7}, {'x': 11, 'y': 8}, {'x': 11, 'y': 9}, {'x': 11, 'y': 10}, {'x': 11, 'y': 11}]}, {'$type': 'add_object', 'name': 'vase_02', 'url': 'https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/vase_02', 'scale_factor': 1.0, 'position': {'x': -2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'category': 'vase', 'id': 13402724}, {'$type': 'add_object', 'name': 'rh10', 'url': 'https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/rh10', 'scale_factor': 0.1, 'position': {'x': -1, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'category': 'toy', 'id': 9453548}, {'$type': 'add_object', 'name': 'iron_box', 'url': 'https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/iron_box', 'scale_factor': 1.0, 'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'category': 'box', 'id': 13570877}, {'$type': 'send_log_messages'}]
[{'$type': 'terminate'}]
```

## Play back commands

To recreate the exact same scene, set `record=False`:

```python
from tdw.controller import Controller
from tdw.add_ons.logger import Logger

c = Controller()
logger = Logger(record=False, path="log.json")
c.add_ons.append(logger)

while len(logger.playback) >= 0:
    if len(logger.playback) > 0:
        print(logger.playback[0])
    c.communicate([])
```

Output:

```
[{'$type': 'create_exterior_walls', 'walls': [{'x': 0, 'y': 0}, {'x': 0, 'y': 1}, {'x': 0, 'y': 2}, {'x': 0, 'y': 3}, {'x': 0, 'y': 4}, {'x': 0, 'y': 5}, {'x': 0, 'y': 6}, {'x': 0, 'y': 7}, {'x': 0, 'y': 8}, {'x': 0, 'y': 9}, {'x': 0, 'y': 10}, {'x': 0, 'y': 11}, {'x': 1, 'y': 0}, {'x': 1, 'y': 11}, {'x': 2, 'y': 0}, {'x': 2, 'y': 11}, {'x': 3, 'y': 0}, {'x': 3, 'y': 11}, {'x': 4, 'y': 0}, {'x': 4, 'y': 11}, {'x': 5, 'y': 0}, {'x': 5, 'y': 11}, {'x': 6, 'y': 0}, {'x': 6, 'y': 11}, {'x': 7, 'y': 0}, {'x': 7, 'y': 11}, {'x': 8, 'y': 0}, {'x': 8, 'y': 11}, {'x': 9, 'y': 0}, {'x': 9, 'y': 11}, {'x': 10, 'y': 0}, {'x': 10, 'y': 11}, {'x': 11, 'y': 0}, {'x': 11, 'y': 1}, {'x': 11, 'y': 2}, {'x': 11, 'y': 3}, {'x': 11, 'y': 4}, {'x': 11, 'y': 5}, {'x': 11, 'y': 6}, {'x': 11, 'y': 7}, {'x': 11, 'y': 8}, {'x': 11, 'y': 9}, {'x': 11, 'y': 10}, {'x': 11, 'y': 11}]}, {'$type': 'add_object', 'name': 'vase_02', 'url': 'https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/vase_02', 'scale_factor': 1.0, 'position': {'x': -2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'category': 'vase', 'id': 13402724}, {'$type': 'add_object', 'name': 'rh10', 'url': 'https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/rh10', 'scale_factor': 0.1, 'position': {'x': -1, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'category': 'toy', 'id': 9453548}, {'$type': 'add_object', 'name': 'iron_box', 'url': 'https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/iron_box', 'scale_factor': 1.0, 'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'category': 'box', 'id': 13570877}, {'$type': 'send_log_messages'}]
[{'$type': 'terminate'}]
```

***

***

**This is the last document in the "Troubleshooting" guide.**

[Return to the README](../../../README.md)

***

Python API:

- [`Logger`](../../python/add_ons/logger.md)